#include "UI/BRHUD.h"
#include "UI/BRHUDWidget.h"
#include "Blueprint/UserWidget.h"
#include "GameFramework/PlayerController.h"

ABRHUD::ABRHUD()
{
    MainHUDClass = UBRHUDWidget::StaticClass();
}

void ABRHUD::ShowMainMenu()
{
    APlayerController* PC = GetOwningPlayerController();
    if (!PC)
    {
        return;
    }

    // Remove active HUD widget if visible
    if (MainHUDWidget && MainHUDWidget->IsInViewport())
    {
        MainHUDWidget->RemoveFromParent();
    }

    // Recreate menu widget if class changed
    if (MainMenuWidget && MainMenuWidget->GetClass() != MainMenuClass)
    {
        MainMenuWidget->RemoveFromParent();
        MainMenuWidget = nullptr;
    }

    // Create widget if not already created
    if (!MainMenuWidget && MainMenuClass)
    {
        MainMenuWidget = CreateWidget<UUserWidget>(PC, MainMenuClass);
    }

    if (MainMenuWidget)
    {
        if (!MainMenuWidget->IsInViewport())
        {
            MainMenuWidget->AddToViewport();
        }
        MainMenuWidget->SetVisibility(ESlateVisibility::Visible);

        FInputModeUIOnly InputMode;
        InputMode.SetWidgetToFocus(MainMenuWidget->TakeWidget());
        InputMode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
        PC->SetInputMode(InputMode);
    }
    else
    {
        FInputModeUIOnly InputMode;
        InputMode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
        PC->SetInputMode(InputMode);
    }

    PC->bShowMouseCursor = true;
}

void ABRHUD::ShowHUD()
{
    APlayerController* PC = GetOwningPlayerController();
    if (!PC)
    {
        return;
    }

    // Remove active Main Menu widget if visible
    if (MainMenuWidget && MainMenuWidget->IsInViewport())
    {
        MainMenuWidget->RemoveFromParent();
    }

    // Recreate HUD widget if class changed
    if (MainHUDWidget && MainHUDWidget->GetClass() != MainHUDClass)
    {
        MainHUDWidget->RemoveFromParent();
        MainHUDWidget = nullptr;
    }

    // Create widget if not already created
    if (!MainHUDWidget && MainHUDClass)
    {
        MainHUDWidget = CreateWidget<UUserWidget>(PC, MainHUDClass);
    }

    if (MainHUDWidget)
    {
        if (!MainHUDWidget->IsInViewport())
        {
            MainHUDWidget->AddToViewport();
        }
        MainHUDWidget->SetVisibility(ESlateVisibility::Visible);
    }

    FInputModeGameOnly InputMode;
    PC->SetInputMode(InputMode);
    PC->bShowMouseCursor = false;
}

UBRHUDWidget* ABRHUD::GetBRHUDWidget() const
{
    return Cast<UBRHUDWidget>(MainHUDWidget);
}

