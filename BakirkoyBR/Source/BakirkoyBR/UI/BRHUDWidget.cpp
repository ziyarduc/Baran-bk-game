#include "UI/BRHUDWidget.h"
#include "Character/BRCharacter.h"
#include "Character/BRHealthComponent.h"
#include "Weapons/BRWeaponBase.h"
#include "Storm/BRStormCircle.h"
#include "Core/BRGameState.h"
#include "Components/ProgressBar.h"
#include "Components/TextBlock.h"
#include "EngineUtils.h"

UBRHUDWidget::UBRHUDWidget(const FObjectInitializer& ObjectInitializer)
	: Super(ObjectInitializer)
{
	CurrentHealth = 100.f;
	MaxHealth = 100.f;
	HealthPercent = 1.f;
	CurrentShield = 0.f;
	MaxShield = 100.f;
	ShieldPercent = 0.f;
	CurrentAmmo = 0;
	ReserveAmmo = 0;
	CurrentStormPhase = 0;
	StormRemainingTime = 0.f;
	bIsStormShrinking = false;
}

void UBRHUDWidget::NativeConstruct()
{
	Super::NativeConstruct();

	if (ABRCharacter* BRChar = Cast<ABRCharacter>(GetOwningPlayerPawn()))
	{
		BindToCharacter(BRChar);
	}

	BindToStorm();
	UpdateStormFromWorld();
}

void UBRHUDWidget::NativeDestruct()
{
	UnbindFromCharacter();

	if (CachedStormCircle.IsValid())
	{
		CachedStormCircle->OnStormPhaseChanged.RemoveDynamic(this, &UBRHUDWidget::HandleStormPhaseChanged);
		CachedStormCircle.Reset();
	}

	Super::NativeDestruct();
}

void UBRHUDWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);

	// Late-binding fallback in case pawn was not possessed during NativeConstruct
	if (!BoundCharacter.IsValid())
	{
		if (ABRCharacter* BRChar = Cast<ABRCharacter>(GetOwningPlayerPawn()))
		{
			BindToCharacter(BRChar);
		}
	}

	UpdateStormFromWorld();
}

void UBRHUDWidget::BindToCharacter(ABRCharacter* InCharacter)
{
	if (BoundCharacter.Get() == InCharacter && InCharacter != nullptr)
	{
		return;
	}

	UnbindFromCharacter();

	if (!InCharacter)
	{
		return;
	}

	BoundCharacter = InCharacter;

	// Bind to health component
	if (InCharacter->HealthComponent)
	{
		BindToHealthComponent(InCharacter->HealthComponent);
	}

	// Listen for active weapon swaps
	InCharacter->OnWeaponEquipped.AddDynamic(this, &UBRHUDWidget::HandleWeaponEquipped);

	// Bind to currently equipped weapon if any
	if (ABRWeaponBase* CurrentWeapon = InCharacter->GetCurrentWeapon())
	{
		BindToWeapon(CurrentWeapon);
	}
	else
	{
		UpdateAmmo(0, 0);
	}
}

void UBRHUDWidget::UnbindFromCharacter()
{
	if (BoundCharacter.IsValid())
	{
		BoundCharacter->OnWeaponEquipped.RemoveDynamic(this, &UBRHUDWidget::HandleWeaponEquipped);
	}

	UnbindFromHealthComponent();
	UnbindFromWeapon();
	BoundCharacter.Reset();
}

void UBRHUDWidget::BindToHealthComponent(UBRHealthComponent* InHealthComp)
{
	if (BoundHealthComponent.Get() == InHealthComp && InHealthComp != nullptr)
	{
		return;
	}

	UnbindFromHealthComponent();

	if (!InHealthComp)
	{
		return;
	}

	BoundHealthComponent = InHealthComp;
	InHealthComp->OnHealthChanged.AddDynamic(this, &UBRHUDWidget::HandleHealthChanged);

	// Initial values
	UpdateHealth(InHealthComp->GetHealth(), InHealthComp->GetMaxHealth());
	UpdateShield(InHealthComp->GetShield(), InHealthComp->GetMaxShield());
}

void UBRHUDWidget::UnbindFromHealthComponent()
{
	if (BoundHealthComponent.IsValid())
	{
		BoundHealthComponent->OnHealthChanged.RemoveDynamic(this, &UBRHUDWidget::HandleHealthChanged);
		BoundHealthComponent.Reset();
	}
}

void UBRHUDWidget::BindToWeapon(ABRWeaponBase* InWeapon)
{
	if (BoundWeapon.Get() == InWeapon && InWeapon != nullptr)
	{
		return;
	}

	UnbindFromWeapon();

	if (!InWeapon)
	{
		UpdateAmmo(0, 0);
		return;
	}

	BoundWeapon = InWeapon;
	InWeapon->OnAmmoChanged.AddDynamic(this, &UBRHUDWidget::HandleAmmoChanged);

	// Initial ammo
	UpdateAmmo(InWeapon->GetCurrentAmmo(), InWeapon->GetReserveAmmo());
}

void UBRHUDWidget::UnbindFromWeapon()
{
	if (BoundWeapon.IsValid())
	{
		BoundWeapon->OnAmmoChanged.RemoveDynamic(this, &UBRHUDWidget::HandleAmmoChanged);
		BoundWeapon.Reset();
	}
}

void UBRHUDWidget::BindToStorm()
{
	if (CachedStormCircle.IsValid())
	{
		return;
	}

	if (UWorld* World = GetWorld())
	{
		for (TActorIterator<ABRStormCircle> It(World); It; ++It)
		{
			if (ABRStormCircle* Storm = *It)
			{
				CachedStormCircle = Storm;
				Storm->OnStormPhaseChanged.AddDynamic(this, &UBRHUDWidget::HandleStormPhaseChanged);
				break;
			}
		}
	}
}

void UBRHUDWidget::UpdateStormFromWorld()
{
	if (!CachedStormCircle.IsValid())
	{
		BindToStorm();
	}

	if (CachedStormCircle.IsValid())
	{
		UpdateStormInfo(
			CachedStormCircle->GetCurrentPhase(),
			CachedStormCircle->GetRemainingPhaseTime(),
			CachedStormCircle->IsShrinking()
		);
	}
	else if (UWorld* World = GetWorld())
	{
		if (ABRGameState* GameState = World->GetGameState<ABRGameState>())
		{
			UpdateStormInfo(
				GameState->StormPhase,
				0.f,
				GameState->bIsStormShrinking
			);
		}
	}
}

void UBRHUDWidget::UpdateHealth(float NewHealth, float InMaxHealth)
{
	MaxHealth = FMath::Max(1.f, InMaxHealth);
	CurrentHealth = FMath::Clamp(NewHealth, 0.f, MaxHealth);
	HealthPercent = FMath::Clamp(CurrentHealth / MaxHealth, 0.f, 1.f);

	if (HealthProgressBar)
	{
		HealthProgressBar->SetPercent(HealthPercent);
	}

	if (HealthText)
	{
		HealthText->SetText(FText::AsNumber(FMath::RoundToInt(CurrentHealth)));
	}

	OnHealthUpdated(CurrentHealth, MaxHealth, HealthPercent);
}

void UBRHUDWidget::UpdateShield(float NewShield, float InMaxShield)
{
	MaxShield = FMath::Max(1.f, InMaxShield);
	CurrentShield = FMath::Clamp(NewShield, 0.f, MaxShield);
	ShieldPercent = FMath::Clamp(CurrentShield / MaxShield, 0.f, 1.f);

	if (ShieldProgressBar)
	{
		ShieldProgressBar->SetPercent(ShieldPercent);
	}

	if (ShieldText)
	{
		ShieldText->SetText(FText::AsNumber(FMath::RoundToInt(CurrentShield)));
	}

	OnShieldUpdated(CurrentShield, MaxShield, ShieldPercent);
}

void UBRHUDWidget::UpdateAmmo(int32 InCurrentAmmo, int32 InReserveAmmo)
{
	CurrentAmmo = FMath::Max(0, InCurrentAmmo);
	ReserveAmmo = FMath::Max(0, InReserveAmmo);

	if (AmmoCurrentText)
	{
		AmmoCurrentText->SetText(FText::AsNumber(CurrentAmmo));
	}

	if (AmmoReserveText)
	{
		AmmoReserveText->SetText(FText::AsNumber(ReserveAmmo));
	}

	if (AmmoTextWidget)
	{
		AmmoTextWidget->SetText(GetAmmoText());
	}

	OnAmmoUpdated(CurrentAmmo, ReserveAmmo);
}

void UBRHUDWidget::UpdateStormInfo(int32 InPhase, float InRemainingTime, bool bInShrinking)
{
	CurrentStormPhase = InPhase;
	StormRemainingTime = FMath::Max(0.f, InRemainingTime);
	bIsStormShrinking = bInShrinking;

	if (StormTimerTextWidget)
	{
		StormTimerTextWidget->SetText(GetStormTimerText());
	}

	if (StormPhaseTextWidget)
	{
		StormPhaseTextWidget->SetText(GetStormPhaseText());
	}

	OnStormInfoUpdated(CurrentStormPhase, StormRemainingTime, bIsStormShrinking);
}

FText UBRHUDWidget::GetAmmoText() const
{
	return FText::FromString(FString::Printf(TEXT("%d / %d"), CurrentAmmo, ReserveAmmo));
}

FText UBRHUDWidget::GetStormTimerText() const
{
	const int32 TotalSeconds = FMath::Max(0, FMath::FloorToInt(StormRemainingTime));
	const int32 Minutes = TotalSeconds / 60;
	const int32 Seconds = TotalSeconds % 60;
	return FText::FromString(FString::Printf(TEXT("%02d:%02d"), Minutes, Seconds));
}

FText UBRHUDWidget::GetStormPhaseText() const
{
	if (bIsStormShrinking)
	{
		return FText::FromString(FString::Printf(TEXT("Phase %d: Storm Shrinking"), CurrentStormPhase + 1));
	}
	return FText::FromString(FString::Printf(TEXT("Phase %d: Safe Zone Closes In"), CurrentStormPhase + 1));
}

void UBRHUDWidget::HandleHealthChanged(float NewHealth, float NewShield, const FBRDamageInfo& DamageInfo)
{
	const float InMaxHealth = BoundHealthComponent.IsValid() ? BoundHealthComponent->GetMaxHealth() : MaxHealth;
	const float InMaxShield = BoundHealthComponent.IsValid() ? BoundHealthComponent->GetMaxShield() : MaxShield;

	UpdateHealth(NewHealth, InMaxHealth);
	UpdateShield(NewShield, InMaxShield);
}

void UBRHUDWidget::HandleWeaponEquipped(ABRWeaponBase* NewWeapon)
{
	BindToWeapon(NewWeapon);
}

void UBRHUDWidget::HandleAmmoChanged(int32 InCurrentAmmo, int32 InReserveAmmo)
{
	UpdateAmmo(InCurrentAmmo, InReserveAmmo);
}

void UBRHUDWidget::HandleStormPhaseChanged(int32 NewPhase)
{
	if (CachedStormCircle.IsValid())
	{
		UpdateStormInfo(NewPhase, CachedStormCircle->GetRemainingPhaseTime(), CachedStormCircle->IsShrinking());
	}
	else
	{
		UpdateStormInfo(NewPhase, StormRemainingTime, bIsStormShrinking);
	}
}
