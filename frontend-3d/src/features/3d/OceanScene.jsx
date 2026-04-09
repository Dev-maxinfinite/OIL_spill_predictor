import React, { useRef } from 'react';
import { useFrame, extend } from '@react-three/fiber';
import { shaderMaterial } from '@react-three/drei';
import * as THREE from 'three';

// A simple procedural water shader for the "Ocean" background
const WaterMaterial = shaderMaterial(
  {
    uTime: 0,
    uColorBase: new THREE.Color('#050a15'),
    uColorHighlight: new THREE.Color('#0051ff'),
  },
  // Vertex Shader
  `
    uniform float uTime;
    varying float vZ;
    void main() {
      vec4 modelPosition = modelMatrix * vec4(position, 1.0);
      
      // Procedural wave math
      float elevation = sin(modelPosition.x * 2.0 + uTime) * 0.1 
                      + sin(modelPosition.z * 1.5 + uTime * 0.8) * 0.1;
      
      modelPosition.y += elevation;
      vZ = elevation;

      vec4 viewPosition = viewMatrix * modelPosition;
      gl_Position = projectionMatrix * viewPosition;
    }
  `,
  // Fragment Shader
  `
    uniform vec3 uColorBase;
    uniform vec3 uColorHighlight;
    varying float vZ;
    
    void main() {
      // Mix colors based on elevation
      float mixStrength = (vZ + 0.2) * 2.5; 
      vec3 color = mix(uColorBase, uColorHighlight, mixStrength);
      gl_FragColor = vec4(color, 1.0);
    }
  `
);

extend({ WaterMaterial });

const OceanScene = () => {
  const materialRef = useRef();

  useFrame((state) => {
    if (materialRef.current) {
      materialRef.current.uTime = state.clock.elapsedTime;
    }
  });

  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1, 0]}>
      <planeGeometry args={[10, 10, 64, 64]} />
      <waterMaterial ref={materialRef} side={THREE.DoubleSide} wireframe={true} />
    </mesh>
  );
};

export default OceanScene;
