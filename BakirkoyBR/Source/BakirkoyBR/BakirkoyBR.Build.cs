using UnrealBuildTool;

public class BakirkoyBR : ModuleRules
{
    public BakirkoyBR(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "InputCore",
            "EnhancedInput",
            "AIModule",
            "NavigationSystem",
            "GameplayTasks",
            "Niagara",
            "UMG",
            "Slate",
            "SlateCore"
        });

        PrivateDependencyModuleNames.AddRange(new string[]
        {
            "NetCore",
            "ReplicationGraph",
            "Slate",
            "SlateCore"
        });
    }
}
