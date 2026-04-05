# TODO - Gaming Tournament & League

## Current Features

- [x] League system with round-robin (home/away)
- [x] Match scheduling and result entry
- [x] Player statistics and history
- [x] Dark/Light theme
- [x] Mock authentication (admin login)

## Future Features

### MK8D Builds Integration
- [ ] Import CSV data from jfmario/mario-kart-8-deluxe-builds
  - [ ] Drivers (characters)
  - [ ] Vehicles
  - [ ] Tires
  - [ ] Gliders
- [ ] Create web interface for builds overview
- [ ] Display "winners" (best build per stat)
- [ ] Integrate with match result entry
  - [ ] Player selects build before match
  - [ ] Optional: track lap/banetid

### Authentication
- [ ] Real user registration with email
- [ ] Email verification with confirmation link
- [ ] Password hashing

### Tournament System
- [ ] Single elimination bracket
- [ ] Double elimination with losers bracket
- [ ] Auto bracket selection based on player count

### Extensibility
- [ ] Support additional competitive games
- [ ] Configurable tournament formats

---

## Notes

- MK8D data source: https://github.com/jfmario/mario-kart-8-deluxe-builds
- Stats: GroundSpeed, WaterSpeed, AirSpeed, AntiGravitySpeed, Acceleration, Weight, Handling, Traction, MiniTurbo
