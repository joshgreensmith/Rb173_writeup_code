//! # Doppler Sweep
//!
//! Simulate a cloud of atoms in a 3D MOT to measure the Doppler temperature limit for laser cooling.
//!
//! The Doppler Limit depends on temperature, see eg https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.61.169.
//!
//! Some parameters of the simulation can be set by writing a configuration file called `doppler.json`. This file
//! allows the user to control parameters, eg detuning. If the file is not written, a default detuning of 0.5 Gamma
//! is used, which corresponds to the minimum Doppler temperature.

extern crate atomecs as lib;
extern crate nalgebra;
use lib::atom::{Atom, AtomicTransition, Force, Mass, Position, Velocity};
use lib::ecs;
use lib::initiate::NewlyCreated;
use lib::integrator::Timestep;
use lib::laser::gaussian::GaussianBeam;
use lib::laser_cooling::force::{EmissionForceConfiguration, EmissionForceOption};
use lib::laser_cooling::photons_scattered::ScatteringFluctuationsOption;
use lib::laser_cooling::CoolingLight;
use lib::magnetic::quadrupole::QuadrupoleField3D;
use lib::output::file;
use lib::output::file::Text;
use lib::shapes::Cuboid;
use lib::sim_region::{SimulationVolume, VolumeType};
use nalgebra::Vector3;
use rand_distr::{Distribution, Normal};
use specs::prelude::*;
use std::fs::read_to_string;
use std::time::Instant;

extern crate serde;
use serde::Deserialize;

#[derive(Deserialize)]
pub struct DopperSimulationConfiguration {
    /// Delta offset for normal distribution of laser beam offsets in each direction, in m.
    pub offset_delta: f64,

    /// Detuning of the lasers
    pub detuning: f64, 
    
    /// Number of simulation steps to evolve for.
    pub number_of_steps: i32,
}
impl Default for DopperSimulationConfiguration {
    fn default() -> Self {
        DopperSimulationConfiguration {
            offset_delta: 0.0,
            detuning: -12.0,
            number_of_steps: 5000,
        }
    }
}

fn main() {
    let now = Instant::now();

    //Load configuration if one exists.
    let read_result = read_to_string("offsets.json");
    let configuration: DopperSimulationConfiguration = match read_result {
        Ok(json_str) => serde_json::from_str(&json_str).unwrap(),
        Err(_) => DopperSimulationConfiguration::default(),
    };

    // Create the simulation world and builder for the ECS dispatcher.
    let mut world = World::new();
    ecs::register_components(&mut world);
    ecs::register_resources(&mut world);
    let mut builder = ecs::create_simulation_dispatcher_builder();

    // Configure simulation output.
    builder = builder.with(
        file::new::<Velocity, Text>("cell_mot_output/vel.txt".to_string(), 5000),
        "",
        &[],
    );

    builder = builder.with(
      file::new::<Position, Text>("cell_mot_output/pos.txt".to_string(), 10),
      "",
      &[],
    );

    let mut dispatcher = builder.build();
    dispatcher.setup(&mut world);

    // Create magnetic field.
    world
        .create_entity()
        .with(QuadrupoleField3D::gauss_per_cm(45.0, Vector3::z()))
        .with(Position {
            pos: Vector3::new(0.0, 0.0, 0.0),
        })
        .build();

    // Create cooling lasers.
    let detuning = configuration.detuning;
    let power = 5.0e-3;
    let radius = 5.0e-3;
    // let beam_centre = Vector3::new(0.0, 0.0, 0.0);

    // Setup offset distribution
    let offset_dist = Normal::new(0.0, configuration.offset_delta).unwrap();
    let mut rng = rand::thread_rng();

    world
        .create_entity()
        .with(GaussianBeam {
            intersection: Vector3::new(
              offset_dist.sample(&mut rng),
              offset_dist.sample(&mut rng),
              offset_dist.sample(&mut rng)
            ),
            e_radius: radius,
            power: power,
            direction: Vector3::new(0.0, 0.0, 1.0),
            rayleigh_range: f64::INFINITY,
            ellipticity: 0.0,
        })
        .with(CoolingLight::for_species(
            AtomicTransition::rubidium(),
            detuning,
            -1,
        ))
        .build();
    world
        .create_entity()
        .with(GaussianBeam {
            intersection: Vector3::new(
              offset_dist.sample(&mut rng),
              offset_dist.sample(&mut rng),
              offset_dist.sample(&mut rng)
            ),
            e_radius: radius,
            power: power,
            direction: Vector3::new(0.0, 0.0, -1.0),
            rayleigh_range: f64::INFINITY,
            ellipticity: 0.0,
        })
        .with(CoolingLight::for_species(
            AtomicTransition::rubidium(),
            detuning,
            -1,
        ))
        .build();
    world
        .create_entity()
        .with(GaussianBeam {
            intersection: Vector3::new(
              offset_dist.sample(&mut rng),
              offset_dist.sample(&mut rng),
              offset_dist.sample(&mut rng)
            ),
            e_radius: radius,
            power: power,
            direction: Vector3::new(1.0 / (2.0_f64.sqrt()), 1.0 / (2.0_f64.sqrt()), 0.0),
            rayleigh_range: f64::INFINITY,
            ellipticity: 0.0,
        })
        .with(CoolingLight::for_species(
            AtomicTransition::rubidium(),
            detuning,
            1,
        ))
        .build();
    world
        .create_entity()
        .with(GaussianBeam {
            intersection: Vector3::new(
              offset_dist.sample(&mut rng),
              offset_dist.sample(&mut rng),
              offset_dist.sample(&mut rng)
            ),
            e_radius: radius,
            power: power,
            direction: Vector3::new(1.0 / (2.0_f64.sqrt()), -1.0 / (2.0_f64.sqrt()), 0.0),
            rayleigh_range: f64::INFINITY,
            ellipticity: 0.0,
        })
        .with(CoolingLight::for_species(
            AtomicTransition::rubidium(),
            detuning,
            1,
        ))
        .build();
    world
        .create_entity()
        .with(GaussianBeam {
            intersection: Vector3::new(
              offset_dist.sample(&mut rng),
              offset_dist.sample(&mut rng),
              offset_dist.sample(&mut rng)
            ),
            e_radius: radius,
            power: power,
            direction: Vector3::new(-1.0 / (2.0_f64.sqrt()), -1.0 / (2.0_f64.sqrt()), 0.0),
            rayleigh_range: f64::INFINITY,
            ellipticity: 0.0,
        })
        .with(CoolingLight::for_species(
            AtomicTransition::rubidium(),
            detuning,
            1,
        ))
        .build();
    world
        .create_entity()
        .with(GaussianBeam {
            intersection: Vector3::new(
              offset_dist.sample(&mut rng),
              offset_dist.sample(&mut rng),
              offset_dist.sample(&mut rng)
            ),
            e_radius: radius,
            power: power,
            direction: Vector3::new(-1.0 / (2.0_f64.sqrt()), 1.0 / (2.0_f64.sqrt()), 0.0),
            rayleigh_range: f64::INFINITY,
            ellipticity: 0.0,
        })
        .with(CoolingLight::for_species(
            AtomicTransition::rubidium(),
            detuning,
            1,
        ))
        .build();

    // Define timestep
    world.insert(Timestep { delta: 1.0e-5 });

    // Create simulation volume to bound atoms in the cell MOT
    let cuboid_pos = Vector3::new(-0.13, 0.0, 0.0);
    let half_width = Vector3::new(0.17, 0.0125, 0.0125);
    world
        .create_entity()
        .with(Position {pos: cuboid_pos})
        .with(Cuboid {
          half_width: half_width
        })
        .with(SimulationVolume {
          volume_type: VolumeType::Inclusive
        })
        .build();


    // Transverse and longitudinal distribution and sample x,y,z
    let pos_dist = Normal::new(0.0, 0.2e-3).unwrap();
    let transverse_vel_dist = Normal::new(0.0, 0.1).unwrap();
    let longitudinal_vel_dist = Normal::new(20.0, 1.0).unwrap();

    // Trial to replicate rb173 diagrams
    // let pos_dist = Normal::new(2.5e-3, 0.1e-3).unwrap();
    // let transverse_vel_dist = Normal::new(0.0, 0.0).unwrap();
    // let longitudinal_vel_dist = Normal::new(20.0, 1.0).unwrap();

    let mut rng = rand::thread_rng();

    // Add atoms
    for _ in 0..1000 {
      world
          .create_entity()
          .with(Position {
              pos: Vector3::new(
                  // Centre distribution at edge of sim region
                  -12.99e-2,
                  pos_dist.sample(&mut rng),
                  pos_dist.sample(&mut rng),
              ),
          })
          .with(Velocity {
              vel: Vector3::new(
                  longitudinal_vel_dist.sample(&mut rng),
                  transverse_vel_dist.sample(&mut rng),
                  transverse_vel_dist.sample(&mut rng),
              ),
          })
          .with(Force::new())
          .with(Mass { value: 87.0 })
          .with(AtomicTransition::rubidium())
          .with(Atom)
          .with(NewlyCreated)
          .build();
    }

    // Enable fluctuation options
    //  * Allow photon numbers to fluctuate.
    //  * Allow random force from emission of photons.
    world.insert(EmissionForceOption::On(EmissionForceConfiguration {
        explicit_threshold: 5,
    }));
    world.insert(ScatteringFluctuationsOption::On);

    // Run the simulation for a number of steps.
    for _i in 0..configuration.number_of_steps {
        dispatcher.dispatch(&mut world);
        world.maintain();
    }

    println!("Simulation completed in {} ms.", now.elapsed().as_millis());
}
