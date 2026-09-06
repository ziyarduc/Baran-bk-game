# Compile Test Protocol

## Conceptual Compile Validation

Since we cannot run an actual UE5 compiler, perform these manual checks:

### 1. Include Resolution
For every `#include "SomeFile.h"` in a .cpp or .h file:
- Verify the target file exists in the expected path
- Verify no circular include chains
- Verify .generated.h is always the LAST include in its header

### 2. Forward Declaration Check
For every forward declaration (`class ABRSomeClass;`):
- Verify the actual class declaration exists somewhere in the project
- Verify the .cpp file includes the full header (not just forward declaration)

### 3. GENERATED_BODY Validation
For every UCLASS, USTRUCT, UENUM:
- Verify GENERATED_BODY() is present
- Verify the matching .generated.h is included in the header

### 4. Replication Completeness
For every UPROPERTY(Replicated) or UPROPERTY(ReplicatedUsing=...):
- Verify GetLifetimeReplicatedProps is implemented in the .cpp
- Verify DOREPLIFETIME macro includes the property
- If ReplicatedUsing, verify the OnRep_ callback function exists

### 5. API Contract Validation
When a .cpp file calls a function from another module:
- Verify the function exists with the expected signature
- Verify the function's UFUNCTION specifiers are appropriate (e.g., BlueprintCallable if called from Blueprint)
- Verify the return type and parameter types match
