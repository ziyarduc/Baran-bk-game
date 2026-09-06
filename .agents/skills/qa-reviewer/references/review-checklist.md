# Review Checklist

Use this checklist for every code review:

## 1. File Structure
- [ ] Header has #pragma once
- [ ] Includes ordered: CoreMinimal → UE → Project → Generated
- [ ] .cpp includes its own .h first

## 2. Class Declaration
- [ ] UCLASS() macro with appropriate specifiers
- [ ] GENERATED_BODY() present
- [ ] BR prefix on class name
- [ ] BAKIRKOYBR_API export macro

## 3. Properties
- [ ] All UPROPERTY have Category
- [ ] Replicated props have ReplicatedUsing or just Replicated
- [ ] EditDefaultsOnly for data-driven values
- [ ] VisibleAnywhere for runtime state

## 4. Functions
- [ ] UFUNCTION for all Blueprint-exposed functions
- [ ] Server/Client/NetMulticast RPCs properly marked
- [ ] Virtual functions use override keyword
- [ ] Const correctness on getter functions

## 5. STD Alignment
- [ ] Damage values match STD weapon table
- [ ] Timing values match STD (reload, ADS, cast times)
- [ ] State machine transitions match STD FSM diagram
- [ ] No indoor/interior code

## 6. Architecture
- [ ] Code stays in its designated module folder
- [ ] Shared types in Data/ only
- [ ] No circular #include dependencies
- [ ] Dependencies follow the module graph
