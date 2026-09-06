# Code Standards Checklist

## Mandatory Checks
- [ ] All classes prefixed with BR (ABR*, UBR*, FBR*, EBR*)
- [ ] #pragma once in every header
- [ ] .generated.h included as LAST include in header
- [ ] GENERATED_BODY() macro in every UCLASS/USTRUCT
- [ ] No raw new/delete — use NewObject, CreateDefaultSubobject, MakeShared
- [ ] No using namespace in headers
- [ ] No std:: containers for UObject-holding collections (use TArray, TMap, TSet)
- [ ] All exposed properties have UPROPERTY with appropriate specifiers
- [ ] All exposed functions have UFUNCTION with appropriate specifiers
- [ ] Replicated properties have DOREPLIFETIME in GetLifetimeReplicatedProps
- [ ] Server RPCs validate all input parameters
- [ ] No gameplay logic in constructors
- [ ] Forward declarations in headers, includes in .cpp
