import { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, MeshTransmissionMaterial, PerspectiveCamera, Environment, ContactShadows } from '@react-three/drei';
import * as THREE from 'three';

const GlassCore = () => {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = state.clock.getElapsedTime() * 0.15;
      meshRef.current.rotation.x = state.clock.getElapsedTime() * 0.1;
    }
  });

  return (
    <Float speed={2.5} rotationIntensity={0.4} floatIntensity={0.8}>
      <mesh ref={meshRef} position={[0, 0, 0]} scale={1.8}>
        {/* Anti-gravity abstract knot shape */}
        <torusKnotGeometry args={[1, 0.35, 256, 64]} />
        <MeshTransmissionMaterial
          backside
          samples={4}
          thickness={1.5}
          chromaticAberration={0.4}
          anisotropy={0.3}
          distortion={0.5}
          distortionScale={0.3}
          temporalDistortion={0.1}
          iridescence={1}
          iridescenceIOR={1.5}
          color="#ffffff"
          attenuationColor="#e2e8f0"
          attenuationDistance={0.5}
        />
      </mesh>
    </Float>
  );
};

export const Scene3D = () => {
  return (
    <div className="absolute inset-0 -z-10 h-full w-full bg-[#FDFDFE]">
      <Canvas dpr={[1, 2]}>
        <PerspectiveCamera makeDefault position={[0, 0, 8]} fov={45} />
        
        <ambientLight intensity={1.5} />
        <directionalLight position={[10, 10, 10]} intensity={2} />
        <directionalLight position={[-10, 10, -10]} intensity={1} color="#f8fafc" />
        
        {/* Ultra-realistic studio lighting reflections */}
        <Environment preset="city" />
        
        <GlassCore />
        
        {/* Soft, realistic shadow below the floating object */}
        <ContactShadows position={[0, -3.5, 0]} opacity={0.6} scale={15} blur={2.5} far={4.5} color="#94a3b8" />
      </Canvas>
    </div>
  );
};
