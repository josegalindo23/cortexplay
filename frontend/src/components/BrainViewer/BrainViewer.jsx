/**
 * BrainViewer — 3D Brain Visualization Component
 *
 * Renders the fsaverage5 cortical surface mesh using Three.js.
 * Vertex colors are mapped from fMRI activation values using
 * a plasma colormap, matching scientific visualization standards.
 *
 * Props:
 *   activations: Float32Array of length 20484 — one value per vertex
 */

import { useRef, useEffect, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import * as THREE from 'three'

// ---------------------------------------------------------------------------
// Plasma colormap — maps activation [0,1] to RGB
// Based on matplotlib's plasma colormap used in neuroimaging
// ---------------------------------------------------------------------------
function plasmaColor(t) {
  t = Math.max(0, Math.min(1, t))
  const r = Math.min(1, 0.05 + 1.09 * t)
  const g = Math.max(0, 0.03 * Math.sin(3.14 * t))
  const b = Math.max(0, 0.85 - 1.1 * t)
  return [r, g, b]
}

// ---------------------------------------------------------------------------
// Normalize activation array from z-score to [0, 1]
// ---------------------------------------------------------------------------
function normalizeActivations(activations) {
  const min = Math.min(...activations)
  const max = Math.max(...activations)
  const range = max - min || 1
  return activations.map(v => (v - min) / range)
}

// ---------------------------------------------------------------------------
// Brain Mesh — renders one hemisphere
// ---------------------------------------------------------------------------
function BrainHemisphere({ vertices, faces, activations, side }) {
  const meshRef = useRef()

  const geometry = useMemo(() => {
    const geo = new THREE.BufferGeometry()

    // Flatten vertices: [[x,y,z], ...] → Float32Array
    const positions = new Float32Array(vertices.flat())
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3))

    // Flatten faces: [[a,b,c], ...] → Uint32Array
    const indices = new Uint32Array(faces.flat())
    geo.setIndex(new THREE.BufferAttribute(indices, 1))

    // Initialize vertex colors to gray
    const colors = new Float32Array(vertices.length * 3).fill(0.4)
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3))

    geo.computeVertexNormals()
    return geo
  }, [vertices, faces])

  // Update vertex colors when activations change
  useEffect(() => {
    if (!activations || !geometry) return

    const normalized = normalizeActivations(activations)
    const colors = geometry.attributes.color.array

    for (let i = 0; i < normalized.length; i++) {
      const [r, g, b] = plasmaColor(normalized[i])
      colors[i * 3]     = r
      colors[i * 3 + 1] = g
      colors[i * 3 + 2] = b
    }

    geometry.attributes.color.needsUpdate = true
  }, [activations, geometry])

  // Offset hemispheres slightly apart
  const offsetX = side === 'left' ? -1 : 1

  return (
    <mesh
      ref={meshRef}
      geometry={geometry}
      position={[offsetX, 0, 0]}
    >
      <meshPhongMaterial
        vertexColors
        shininess={30}
        specular={new THREE.Color(0.1, 0.1, 0.1)}
      />
    </mesh>
  )
}

// ---------------------------------------------------------------------------
// Scene — contains both hemispheres + auto-rotation
// ---------------------------------------------------------------------------
function BrainScene({ surfaceData, activations }) {
  const groupRef = useRef()

  useFrame((state, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * 0.15
    }
  })

  if (!surfaceData) return null

  const leftActivations  = activations?.slice(0, 10242)
  const rightActivations = activations?.slice(10242, 20484)

  return (
    <group ref={groupRef}>
      <BrainHemisphere
        vertices={surfaceData.left.vertices}
        faces={surfaceData.left.faces}
        activations={leftActivations}
        side="left"
      />
      <BrainHemisphere
        vertices={surfaceData.right.vertices}
        faces={surfaceData.right.faces}
        activations={rightActivations}
        side="right"
      />
    </group>
  )
}

// ---------------------------------------------------------------------------
// BrainViewer — main exported component
// ---------------------------------------------------------------------------
export default function BrainViewer({ surfaceData, activations }) {
  return (
    <div className="w-full h-full">
      <Canvas
        camera={{ position: [0, 0, 120], fov: 45 }}
        gl={{ antialias: true }}
      >
        {/* Lighting */}
        <ambientLight intensity={0.4} />
        <directionalLight position={[10, 10, 10]} intensity={0.8} />
        <directionalLight position={[-10, -10, -5]} intensity={0.3} />

        {/* Brain */}
        <BrainScene
          surfaceData={surfaceData}
          activations={activations}
        />

        {/* Orbital controls — user can rotate, zoom, pan */}
        <OrbitControls
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          autoRotate={false}
        />
      </Canvas>
    </div>
  )
}