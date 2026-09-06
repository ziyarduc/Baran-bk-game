#pragma once
#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "BRHUD.generated.h"

class UUserWidget;
class UBRHUDWidget;

UCLASS()
class BAKIRKOYBR_API ABRHUD : public AHUD
{
    GENERATED_BODY()

public:
    ABRHUD();

    /** Widget class to use for the main in-game HUD */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "UI")
    TSubclassOf<UUserWidget> MainHUDClass;

    /** Widget class to use for the main menu */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "UI")
    TSubclassOf<UUserWidget> MainMenuClass;

    /** Active instance of the main in-game HUD widget */
    UPROPERTY(BlueprintReadOnly, Category = "UI")
    TObjectPtr<UUserWidget> MainHUDWidget;

    /** Active instance of the main menu widget */
    UPROPERTY(BlueprintReadOnly, Category = "UI")
    TObjectPtr<UUserWidget> MainMenuWidget;

    /** Displays the main menu and switches input to UI Only with visible mouse cursor */
    UFUNCTION(BlueprintCallable, Category = "UI")
    void ShowMainMenu();

    /** Displays the in-game HUD and switches input to Game Only with hidden mouse cursor */
    UFUNCTION(BlueprintCallable, Category = "UI")
    void ShowHUD();

    /** Helper getter for the active Main HUD widget */
    UFUNCTION(BlueprintPure, Category = "UI")
    UUserWidget* GetMainHUDWidget() const { return MainHUDWidget; }

    /** Helper getter for the active Main HUD widget cast to UBRHUDWidget */
    UFUNCTION(BlueprintPure, Category = "UI")
    UBRHUDWidget* GetBRHUDWidget() const;

    /** Helper getter for the active Main Menu widget */
    UFUNCTION(BlueprintPure, Category = "UI")
    UUserWidget* GetMainMenuWidget() const { return MainMenuWidget; }
};
