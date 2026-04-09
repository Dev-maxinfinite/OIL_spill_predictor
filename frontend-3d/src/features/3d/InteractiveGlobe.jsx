import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Sphere } from '@react-three/drei';

const InteractiveGlobe = () => {
  const globeRef = useRef();

  useFrame((state) => {
    if (globeRef.current) {
      globeRef.current.rotation.y = state.clock.elapsedTime * 0.1;
    }
  });

  return (
    <group ref={globeRef}>
      {/* Holographic glowing wireframe globe */}
      <Sphere args={[2, 64, 64]}>
        <meshBasicMaterial 
          color="#00f0ff" 
          wireframe={true} 
          transparent={true} 
          opacity={0.3} 
        />
      </Sphere>
      
      {/* Core dark sphere */}
      <Sphere args={[1.95, 32, 32]}>
        <meshBasicMaterial color="#050a15" />
      </Sphere>

      {/* Simulated "oil spill" anomaly on globe */}
      <mesh position={[1.5, 1, 1]}>
        <sphereGeometry args={[0.05, 16, 16]} />
        <meshBasicMaterial color="#ff2a2a" />
      </mesh>
      
      {/* Pulsing rings around anomaly could be added here */}
    </group>
  );
};

export default InteractiveGlobe;
