# UE5 Best Practices for Bakırköy BR

## Memory Management
- Use `CreateDefaultSubobject<T>()` in constructors for components
- Use `NewObject<T>()` for runtime object creation
- Use `TObjectPtr<T>` instead of raw pointers for UPROPERTY
- Never manually delete UObjects — let GC handle it

## Replication
- Mark replicated properties with `Replicated` or `ReplicatedUsing`
- Use COND_OwnerOnly for properties only the owning client needs
- Use COND_SkipOwner for properties all OTHER clients need
- Server RPCs: validate input, apply state, then replicate
- Client RPCs: for cosmetic feedback only (sound, particles)
- NetMulticast: for effects all clients should see (explosions)

## Performance
- Avoid Tick() when possible — use Timers or Event-driven design
- Use object pooling for projectiles and build piece previews
- Minimize RPC calls — batch updates where possible
- Use relevancy and NetCullDistance for large player counts

## Battle Royale Specific
- 100 players = heavy replication load. Use ReplicationGraph.
- Storm circle updates: replicate only center + radius, not the entire mesh
- Loot: replicate on pickup only, not continuous position updates
- Bot AI: runs entirely on server, no client replication of AI state
