// Import the THREE.js library
import * as THREE from "https://cdn.skypack.dev/three@0.129.0/build/three.module.js";
// To allow for the camera to move around the scene
import { OrbitControls } from "https://cdn.skypack.dev/three@0.129.0/examples/jsm/controls/OrbitControls.js";
// To allow for importing the .gltf file
import { GLTFLoader } from "https://cdn.skypack.dev/three@0.129.0/examples/jsm/loaders/GLTFLoader.js";

let objects = [];
let syncEnabled = true; // Variable to track synchronization state

function showSpinner() {
    document.getElementById('loading-spinner').style.display = 'block';
}

function hideSpinner() {
    document.getElementById('loading-spinner').style.display = 'none';
}

let modelsLoaded = 0;

// Function to load GLTF model
function loadModel(modelPath, canvas, zoomFactor = 1, ambientLightIntensity = 1) {
    showSpinner();

    const scene = new THREE.Scene();

    const camera = new THREE.PerspectiveCamera(75, canvas.clientWidth / canvas.clientHeight, 0.05, 1000);
    camera.position.set(0, 0, 5 * zoomFactor);

    const light = new THREE.AmbientLight(0xffffff, ambientLightIntensity);
    light.position.set(0, 0, 10);
    scene.add(light);

    const loader = new GLTFLoader();
    loader.load(modelPath, function (gltf) {
        const object = gltf.scene;

        const bbox = new THREE.Box3().setFromObject(object);
        const objectSize = new THREE.Vector3();
        bbox.getSize(objectSize);

        let scaleFactor = 1;
        const desiredSize = 2;

        const maxDimension = Math.max(objectSize.x, objectSize.y, objectSize.z);
        const scaleToFit = desiredSize / maxDimension;
        scaleFactor *= scaleToFit;
        object.scale.set(scaleFactor, scaleFactor, scaleFactor);

        scene.add(object);
        objects.push(object);

        const objectPosition = bbox.getCenter(new THREE.Vector3());
        const objectBoundingSphere = bbox.getBoundingSphere(new THREE.Sphere());
        const objectRadius = objectBoundingSphere.radius;
        const cameraDistance = objectRadius * 2 * zoomFactor;
        camera.position.copy(objectPosition.clone().add(new THREE.Vector3(0, 0, cameraDistance)));
        controls.target.copy(objectPosition);

        modelsLoaded++; // Increment the count of loaded models

        if (modelsLoaded === 2) {
            // If both models are loaded, hide the spinner
            hideSpinner();
        }
    });

    const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true });
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    renderer.outputEncoding = THREE.sRGBEncoding;

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
    directionalLight.position.set(0, 1, 1);
    scene.add(directionalLight);

    // Add directional light from the other side
    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.5);
    directionalLight2.position.set(0, 1, -1);
    scene.add(directionalLight2);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.25;

    return { scene, camera, renderer, controls };
}

// Load GLTF models into respective canvases
const canvas1 = document.getElementById('canvas_1');
const canvas2 = document.getElementById('canvas_2');

const { scene: scene1, camera: camera1, renderer: renderer1, controls: controls1 } = loadModel('models/Upperlimb_diffuse/scene.gltf', canvas1, 0.8, 1.0); //zoomFactor, ambientLightIntensity
const { scene: scene2, camera: camera2, renderer: renderer2, controls: controls2 } = loadModel('models/Upperlimb_polarized/scene.gltf', canvas2, 0.9, 1.6); //zoomFactor, ambientLightIntensity



onWindowResize();

function onWindowResize() {
    const width = window.innerWidth / 2; // Divide by 2 for two canvases
    const height = window.innerHeight;

    // Set the width and height of the canvases
    canvas1.width = width;
    canvas1.height = height;
    canvas2.width = width;
    canvas2.height = height;

    // Update the aspect ratio and size of the cameras and renderers
    camera1.aspect = width / height;
    camera1.updateProjectionMatrix();
    renderer1.setSize(width, height);
    controls1.update();

    camera2.aspect = width / height;
    camera2.updateProjectionMatrix();
    renderer2.setSize(width, height);
    controls2.update();
}

window.addEventListener('resize', onWindowResize);

// Function to animate the scenes
// Function to animate the scenes
function animate() {
    requestAnimationFrame(animate);

    // Update controls if synchronization is enabled
    if (syncEnabled) {
        // Temporarily disable controls to prevent conflicts
        controls1.enabled = false;
        controls2.enabled = false;

        // Sync camera positions between canvases
        camera2.position.copy(camera1.position);
        camera2.quaternion.copy(camera1.quaternion);

        // Re-enable controls
        controls1.enabled = true;
        controls2.enabled = true;
    }

    renderer1.render(scene1, camera1);
    renderer2.render(scene2, camera2);
}

animate();

// Function to toggle synchronization
function toggleSync() {
    syncEnabled = !syncEnabled;

    // Get the reference to the sync button
    const syncButton = document.getElementById('sync_button');

    // Update the button style based on syncEnabled state
    if (syncEnabled) {
        // Set button style to green when synchronization is enabled
        syncButton.style.backgroundColor = '#00FF00'; // Green color
    } else {
        // Set button style to red when synchronization is disabled
        syncButton.style.backgroundColor = '#FF0000'; // Red color
    }
}

// Function to initialize the sync button state
function initSyncButton() {
    // Get the reference to the sync button
    const syncButton = document.getElementById('sync_button');

    // Set the initial button style based on syncEnabled state
    if (syncEnabled) {
        // Set button style to green if synchronization is initially enabled
        syncButton.style.backgroundColor = '#00FF00'; // Green color
    } else {
        // Set button style to red if synchronization is initially disabled
        syncButton.style.backgroundColor = '#FF0000'; // Red color
    }
}

// Call the function to initialize the sync button state
initSyncButton();

// Add event listener to button
const syncButton = document.getElementById('sync_button');
syncButton.addEventListener('click', toggleSync);

// Attach event listeners for both controls
controls1.addEventListener('change', () => {
    if (syncEnabled) {
        camera2.position.copy(camera1.position);
        camera2.quaternion.copy(camera1.quaternion);
    }
});

controls2.addEventListener('change', () => {
    if (syncEnabled) {
        camera1.position.copy(camera2.position);
        camera1.quaternion.copy(camera2.quaternion);
    }
});
