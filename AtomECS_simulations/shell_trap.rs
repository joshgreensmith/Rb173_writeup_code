//!

extern crate atomecs;
extern crate nalgebra;
use atomecs::atom::{Atom, Force, Mass, Position, Velocity};
use atomecs::ecs;
use atomecs::ecs::AtomecsDispatcherBuilder;
use atomecs::gravity::ApplyGravityOption;
use atomecs::initiate::NewlyCreated;
use atomecs::integrator::Timestep;
use atomecs::magnetic::quadrupole::QuadrupoleField3D;
use atomecs::output::file;
use atomecs::output::file::Text;
use atomecs::ramp::{Ramp};
use nalgebra::Vector3;
use rand_distr::{Distribution, Normal};
use specs::prelude::*;
use std::time::Instant;
use std::fs::read_to_string;


extern crate rb173;
use rb173::rf_knife::{RFKnife};
use rb173::shell::{ApplyRFDressingForceSystem, ShellTrap};
extern crate serde;
use serde::Deserialize;
extern crate serde_json;

/// Input parameters used to control the simulation.
#[derive(Deserialize)]
pub struct SimulationParameters {
    /// RF field amplitude [Gauss]
    pub rf_amp: f64,
    /// RF frequency [MHz]
    pub rf_frequency: f64,
    /// Quadrupole gradient [G/cm]
    pub quad_grad_initial: f64,
    /// MOT position x [m]
    pub mot_position_x: f64,
    /// MOT position y [m]
    pub mot_position_y: f64,
    /// MOT position z [m]
    pub mot_position_z: f64,
    pub atom_number: i32,
    // Initial velocity of the atoms [m/s]
    pub initial_velocity: f64,
    /// Initial std of the velocity distribution [m/s]
    pub initial_velocity_std: f64,
    /// Initial std of the position distribution [m/s]
    pub initial_pos_std: f64,
    pub timestep: f64,
    pub num_steps: i32,
    pub gravity: bool,
}

fn main() {
    let now = Instant::now();
    let parameters = load_parameters();

    // Create the simulation world and builder for the ECS dispatcher.
    let mut world = World::new();
    ecs::register_components(&mut world);
    ecs::register_resources(&mut world);
    world.register::<ShellTrap>();
    world.register::<RFKnife>();
    world.register::<NewlyCreated>();
    world.register::<Ramp<RFKnife>>();
    world.register::<Ramp<QuadrupoleField3D>>();
    world.register::<Ramp<ShellTrap>>();
    let mut atomecs_builder = AtomecsDispatcherBuilder::new();
    atomecs_builder.add_frame_initialisation_systems();
    atomecs_builder.add_systems();
    atomecs_builder.builder.add(ApplyRFDressingForceSystem {}, "rf_dressing_force", &[]);
    atomecs_builder.add_frame_end_systems();
    let mut builder = atomecs_builder.builder;

    // Configure simulation output.
    builder = builder.with(
      file::new::<Velocity, Text>("shell_trap_output/vel.txt".to_string(), 100),
      "",
      &[],
    );

    builder = builder.with(
      file::new::<Position, Text>("shell_trap_output/pos.txt".to_string(), 10),
      "",
      &[],
    );

    let mut dispatcher = builder.build();
    dispatcher.setup(&mut world);

    //create atoms with gaussian position and velocity distributions
    let mut rng = rand::thread_rng();
    let velocity_dist = Normal::new(parameters.initial_velocity, parameters.initial_velocity_std).unwrap();
    let pos_dist = Normal::new(0.0, parameters.initial_pos_std).unwrap();

    for _i in 0..parameters.atom_number {
        world
            .create_entity()
            .with(Position {
                pos: Vector3::new(
                    parameters.mot_position_x + pos_dist.sample(&mut rng),
                    parameters.mot_position_y + pos_dist.sample(&mut rng),
                    parameters.mot_position_z + pos_dist.sample(&mut rng),
                ),
            })
            .with(Atom)
            .with(Velocity {
                vel: Vector3::new(
                    velocity_dist.sample(&mut rng),
                    velocity_dist.sample(&mut rng),
                    velocity_dist.sample(&mut rng),
                ),
            })
            .with(Force::new())
            .with(NewlyCreated)
            .with(Mass { value: 87.0 })
            .build();
    }

    //Create shell trap
    world
        .create_entity()
        .with(ShellTrap {
            amplitude: parameters.rf_amp,
            frequency: parameters.rf_frequency,
            gradient: parameters.quad_grad_initial,
            bias_field: Vector3::new(0.0, 0.0, 0.0),
        })
        .build();

    // Define timestep
    world.insert(Timestep {
        delta: parameters.timestep,
    });

    if parameters.gravity {
        world.insert(ApplyGravityOption)
    };

    // Run the simulation for a number of steps.
    for _i in 0..parameters.num_steps {
        dispatcher.dispatch(&mut world);
        world.maintain();
    }

    println!("Simulation completed in {} ms.", now.elapsed().as_millis());
}

/// Load simulation parameters from a json-formatted file, named `input.json`.
fn load_parameters() -> SimulationParameters {
    let json_str = read_to_string("input.json").expect(
        "Could not open json-formatted file 'input.json', required to configure the simulation.",
    );
    let parameters: SimulationParameters = serde_json::from_str(&json_str).unwrap();
    return parameters;
}
