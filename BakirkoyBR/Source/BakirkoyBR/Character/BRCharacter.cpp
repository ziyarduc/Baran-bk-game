#include "Character/BRCharacter.h"
#include "Character/BRHealthComponent.h"
#include "Building/BRBuildingComponent.h"
#include "Weapons/BRWeaponBase.h"
#include "Core/BRInputConfig.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputActionValue.h"
#include "InputMappingContext.h"
#include "Engine/LocalPlayer.h"
#include "GameFramework/PlayerController.h"
#include "Net/UnrealNetwork.h"

ABRCharacter::ABRCharacter()
{
    PrimaryActorTick.bCanEverTick = true;

    HealthComponent = CreateDefaultSubobject<UBRHealthComponent>(TEXT("HealthComponent"));
    BuildingComponent = CreateDefaultSubobject<UBRBuildingComponent>(TEXT("BuildingComponent"));

    WeaponSlots.SetNum(5);
}

void ABRCharacter::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);

    DOREPLIFETIME(ABRCharacter, CurrentMovementState);
    DOREPLIFETIME(ABRCharacter, bIsADS);
    DOREPLIFETIME(ABRCharacter, ActiveWeaponSlot);
}

void ABRCharacter::BeginPlay()
{
    Super::BeginPlay();
}

void ABRCharacter::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
}

void ABRCharacter::PawnClientRestart()
{
    Super::PawnClientRestart();

    if (const APlayerController* PC = Cast<APlayerController>(GetController()))
    {
        if (UEnhancedInputLocalPlayerSubsystem* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer()))
        {
            UInputMappingContext* ContextToAdd = DefaultMappingContext;
            if (!ContextToAdd && InputConfig)
            {
                ContextToAdd = InputConfig->DefaultMappingContext;
            }

            if (ContextToAdd)
            {
                Subsystem->AddMappingContext(ContextToAdd, 0);
            }
        }
    }
}

void ABRCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    // Add Input Mapping Context to EnhancedInputLocalPlayerSubsystem
    if (const APlayerController* PC = Cast<APlayerController>(GetController()))
    {
        if (UEnhancedInputLocalPlayerSubsystem* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer()))
        {
            UInputMappingContext* ContextToAdd = DefaultMappingContext;
            if (!ContextToAdd && InputConfig)
            {
                ContextToAdd = InputConfig->DefaultMappingContext;
            }

            if (ContextToAdd)
            {
                Subsystem->AddMappingContext(ContextToAdd, 0);
            }
        }
    }

    // Bind enhanced input actions
    if (UEnhancedInputComponent* EnhancedInputComponent = Cast<UEnhancedInputComponent>(PlayerInputComponent))
    {
        if (InputConfig)
        {
            // Move (Vector2D)
            if (InputConfig->MoveAction)
            {
                EnhancedInputComponent->BindAction(InputConfig->MoveAction, ETriggerEvent::Triggered, this, &ABRCharacter::Input_Move);
            }

            // Look (Vector2D)
            if (InputConfig->LookAction)
            {
                EnhancedInputComponent->BindAction(InputConfig->LookAction, ETriggerEvent::Triggered, this, &ABRCharacter::Input_Look);
            }

            // Jump (Bool)
            if (InputConfig->JumpAction)
            {
                EnhancedInputComponent->BindAction(InputConfig->JumpAction, ETriggerEvent::Started, this, &ABRCharacter::Input_Jump_Started);
                EnhancedInputComponent->BindAction(InputConfig->JumpAction, ETriggerEvent::Completed, this, &ABRCharacter::Input_Jump_Completed);
            }

            // Fire (Bool)
            if (InputConfig->FireAction)
            {
                EnhancedInputComponent->BindAction(InputConfig->FireAction, ETriggerEvent::Started, this, &ABRCharacter::Input_Fire_Started);
                EnhancedInputComponent->BindAction(InputConfig->FireAction, ETriggerEvent::Completed, this, &ABRCharacter::Input_Fire_Completed);
            }

            // Reload (Bool)
            if (InputConfig->ReloadAction)
            {
                EnhancedInputComponent->BindAction(InputConfig->ReloadAction, ETriggerEvent::Started, this, &ABRCharacter::Input_Reload);
            }

            // ADS (Bool)
            if (InputConfig->ADSAction)
            {
                EnhancedInputComponent->BindAction(InputConfig->ADSAction, ETriggerEvent::Started, this, &ABRCharacter::Input_ADS_Started);
                EnhancedInputComponent->BindAction(InputConfig->ADSAction, ETriggerEvent::Completed, this, &ABRCharacter::Input_ADS_Completed);
            }
        }
    }
}

void ABRCharacter::Input_Move(const FInputActionValue& Value)
{
    const FVector2D MovementVector = Value.Get<FVector2D>();

    if (Controller != nullptr)
    {
        const FRotator Rotation = Controller->GetControlRotation();
        const FRotator YawRotation(0.0f, Rotation.Yaw, 0.0f);

        const FVector ForwardDirection = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X);
        const FVector RightDirection = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y);

        AddMovementInput(ForwardDirection, MovementVector.Y);
        AddMovementInput(RightDirection, MovementVector.X);
    }
}

void ABRCharacter::Input_Look(const FInputActionValue& Value)
{
    const FVector2D LookAxisVector = Value.Get<FVector2D>();

    if (Controller != nullptr)
    {
        AddControllerYawInput(LookAxisVector.X);
        AddControllerPitchInput(LookAxisVector.Y);
    }
}

void ABRCharacter::Input_Jump_Started()
{
    Jump();
}

void ABRCharacter::Input_Jump_Completed()
{
    StopJumping();
}

void ABRCharacter::Input_Fire_Started()
{
    if (ABRWeaponBase* CurrentWeapon = GetCurrentWeapon())
    {
        CurrentWeapon->StartFire();
    }
}

void ABRCharacter::Input_Fire_Completed()
{
    if (ABRWeaponBase* CurrentWeapon = GetCurrentWeapon())
    {
        CurrentWeapon->StopFire();
    }
}

void ABRCharacter::Input_Reload()
{
    if (ABRWeaponBase* CurrentWeapon = GetCurrentWeapon())
    {
        CurrentWeapon->Reload();
    }
}

void ABRCharacter::Input_ADS_Started()
{
    SetADS(true);
}

void ABRCharacter::Input_ADS_Completed()
{
    SetADS(false);
}

void ABRCharacter::SetADS(bool bNewADS)
{
    bIsADS = bNewADS;

    if (!HasAuthority())
    {
        ServerSetADS(bNewADS);
    }
}

bool ABRCharacter::ServerSetADS_Validate(bool bNewADS)
{
    return true;
}

void ABRCharacter::ServerSetADS_Implementation(bool bNewADS)
{
    SetADS(bNewADS);
}


void ABRCharacter::EquipWeapon(int32 SlotIndex)
{
    if (!WeaponSlots.IsValidIndex(SlotIndex))
    {
        return;
    }

    ABRWeaponBase* PreviousWeapon = GetCurrentWeapon();
    ABRWeaponBase* NewWeapon = WeaponSlots[SlotIndex];

    // Holster previous weapon if different from the new weapon
    if (PreviousWeapon && PreviousWeapon != NewWeapon)
    {
        PreviousWeapon->Holster();
    }

    // Update the active weapon slot index
    ActiveWeaponSlot = SlotIndex;

    // Attach new weapon to character's hand socket and initialize state
    if (NewWeapon)
    {
        NewWeapon->Equip(this);
    }

    OnWeaponEquipped.Broadcast(NewWeapon);
}

ABRWeaponBase* ABRCharacter::GetCurrentWeapon() const
{
    if (WeaponSlots.IsValidIndex(ActiveWeaponSlot))
    {
        return WeaponSlots[ActiveWeaponSlot];
    }
    return nullptr;
}
