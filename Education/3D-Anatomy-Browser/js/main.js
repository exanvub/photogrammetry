// Import the THREE.js library
import * as THREE from "https://cdn.skypack.dev/three@0.129.0/build/three.module.js";
// To allow for the camera to move around the scene
import { OrbitControls } from "https://cdn.skypack.dev/three@0.129.0/examples/jsm/controls/OrbitControls.js";
// To allow for importing the .gltf file
import { GLTFLoader } from "https://cdn.skypack.dev/three@0.129.0/examples/jsm/loaders/GLTFLoader.js";

// Create a Three.JS Scene
const scene = new THREE.Scene();
// Create a new camera with positions and angles
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.05, 1000);

// Keep the 3D object on a global variable so we can access it later
let object;

// Set which object to render initially based on the selected option in the dropdown menu
let objToRender = document.getElementById('model-select').value;

// Instantiate a loader for the .gltf file
const loader = new GLTFLoader();

// Load the initial model
loadModel(objToRender);

// Function to show the spinner
function showSpinner() {
  document.getElementById('loading-spinner').style.display = 'block';
}

// Function to hide the spinner
function hideSpinner() {
  document.getElementById('loading-spinner').style.display = 'none';
}

function loadModel(modelName) {
  // Show spinner while loading
  showSpinner();

  camera.position.set(0, 0, 5);
  camera.lookAt(0, 0, 0);
  
  // Display loading bar
  document.getElementById('loading-bar').style.display = 'block';

  // Load the file
  loader.load(
    `models/${modelName}/scene.gltf`,
    function (gltf) {
      // If the file is loaded, add it to the scene
      object = gltf.scene;

      // Compute the bounding box of the loaded object to determine its dimensions
      const bbox = new THREE.Box3().setFromObject(object);
      const objectSize = new THREE.Vector3();
      bbox.getSize(objectSize);

      // Calculate the scale factor based on the model name and desired size in the scene
      let scaleFactor = 1; // Default scale factor
      const desiredSize = 2; // Adjust this value as needed

      // Adjust scale factor based on model name
      switch (modelName) {

        case "lowerlimb_2_diffuse":
          scaleFactor = 0.75; // Adjust scale factor as needed
          ambientintensity = 0.8;
          break;

        case "lowerlimb_2_polarized":
          scaleFactor = 0.75; // Adjust scale factor as needed
          ambientintensity = 1.2;
          break;

        case "lowerlimb_diffuse":
          scaleFactor = 1; // Adjust scale factor as needed
          ambientintensity = 0.6; 
          break;
          
        case "lowerlimb_polarized":
          scaleFactor = 0.75; // Adjust scale factor as needed
          ambientintensity = 1.0;
          break;
        
        case "lowerlimb_polarized_Annotations":
          scaleFactor = 0.8; // Adjust scale factor as needed
          ambientintensity = 1.0;
          break;
        case "lowerlimb_diffuse_Annotations":
          scaleFactor = 0.8; // Adjust scale factor as needed
          ambientintensity = 0.5;
          break;

        case "Upperlimb_diffuse":
          scaleFactor = 1; // Adjust scale factor as needed
          ambientintensity = 0.5;
          break;

        case "Upperlimb_diffuse_Annotations":
          scaleFactor = 1; // Adjust scale factor as needed
          ambientintensity = 0.5;
          break;

        case "Upperlimb_diffuse_quiz":
          scaleFactor = 1; // Adjust scale factor as needed
          ambientintensity = 0.5;
          break;

        case "Upperlimb_polarized":
          scaleFactor = 1; // Adjust scale factor as needed
          ambientintensity = 1.2;
          break;

        case "Upperlimb_polarized_Annotations":
          scaleFactor = 1; // Adjust scale factor as needed
          ambientintensity = 1.2;
          break;

        // Add cases for other models as needed
        default:
          break;
      }

      // Set initial ambient light intensity based on model
      ambientLight.intensity = ambientintensity;
      // Update the GUI control for ambient light intensity
      lightsFolder.__controllers[0].updateDisplay(); // Update the display of the first controller in the lightsFolder


      // Adjust the scale of the object to fit within the desired size in the scene
      const maxDimension = Math.max(objectSize.x, objectSize.y, objectSize.z);
      const scaleToFit = desiredSize / maxDimension;
      scaleFactor *= scaleToFit;
      object.scale.set(scaleFactor, scaleFactor, scaleFactor);

      // Adjust the position of the object if necessary
      // For example, to center the object vertically, you can use: object.position.y = -objectSize.y * scaleFactor / 2;

      scene.add(object);

      // Update the camera position and controls target based on the loaded model
      const objectPosition = bbox.getCenter(new THREE.Vector3());
      const objectBoundingSphere = bbox.getBoundingSphere(new THREE.Sphere());
      const objectRadius = objectBoundingSphere.radius;
      const cameraDistance = objectRadius * 2; // Adjust the multiplier as needed
      camera.position.copy(objectPosition.clone().add(new THREE.Vector3(0, 0, cameraDistance)));
      controls.target.copy(objectPosition); // Set controls target to the center of the loaded model

      // Hide the loading bar once the model is loaded
      document.getElementById('loading-bar').style.display = 'none';

      // Hide spinner once loaded
      hideSpinner();
    },
    function (xhr) {
      // While it is loading, update the loading progress bar
      const progress = (xhr.loaded / xhr.total) * 100;
      document.getElementById('loading-progress').style.width = progress + '%';
    },
    function (error) {
      // If there is an error, log it
      console.error(error);
      // Hide spinner in case of error
      hideSpinner();
    }
  );
}


// Add an event listener to the model select dropdown
document.getElementById('model-select').addEventListener('change', function(event) {
  // Get the selected model value
  objToRender = event.target.value;

  // Remove the previous object from the scene if it exists
  if (object) {
    scene.remove(object);
  }
  // Load the selected model
  loadModel(objToRender);
});

// Instantiate a new renderer and set its size
const renderer = new THREE.WebGLRenderer({ alpha: true }); // Alpha: true allows for the transparent background
renderer.setSize(window.innerWidth, window.innerHeight);

// Add the renderer to the DOM
document.getElementById("container3D").appendChild(renderer.domElement);

let ambientintensity = 0.5;

// Add lights to the scene that can be controlled in the GUI
const ambientLight = new THREE.AmbientLight(0xffffff, ambientintensity);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
directionalLight.position.set(0, 1, 1);

scene.add(directionalLight);

// Add directional light from the other side
const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.5);
directionalLight2.position.set(0, 1, -1);

scene.add(directionalLight2);

// Add gui controls for the lights
const gui = new dat.GUI();
const lightsFolder = gui.addFolder("Lights");
lightsFolder.add(ambientLight, "intensity", 0, 2, 0.01).name("Ambient Light Intensity");
lightsFolder.add(directionalLight, "intensity", 0, 2, 0.01).name("Directional Light Intensity");
lightsFolder.open();

// Add controles for directional light position
const directionalLightFolder = lightsFolder.addFolder("Directional Light Position");
directionalLightFolder.add(directionalLight.position, "x", -10, 10, 0.01).name("X");
directionalLightFolder.add(directionalLight.position, "y", -10, 10, 0.01).name("Y");
directionalLightFolder.add(directionalLight.position, "z", -10, 10, 0.01).name("Z");

// Set the container for the GUI
const guiContainer = document.createElement('div');
guiContainer.id = 'gui-container';
document.body.appendChild(guiContainer); // Append GUI container to the body

// Append GUI to the custom container
guiContainer.appendChild(gui.domElement);

renderer.outputEncoding = THREE.sRGBEncoding;

// This adds controls to the camera, so we can rotate / zoom it with the mouse

const controls = new OrbitControls(camera, renderer.domElement);

controls.minDistance = 0.1;
controls.maxDistance = 8;

// Create a raycaster
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();

// Add event listener for mouse movement
// document.addEventListener('pointermove', onPointerMove, false);
window.addEventListener( 'pointerdown', onPointerDown );

window.addEventListener( 'resize', onWindowResize );

function onWindowResize() {

  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();

  renderer.setSize( window.innerWidth, window.innerHeight );

  render();

}

function onPointerDown(event) {

  // event.preventDefault(); // Preventdefault Causes order elements not to work

  // Calculate mouse position in normalized device coordinates
  const rect = renderer.domElement.getBoundingClientRect();
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

  // Cast a ray from the camera's position through the mouse position
  raycaster.setFromCamera(pointer, camera);

  // Calculate objects intersecting the ray
  const intersects = raycaster.intersectObjects(scene.children, true);

  // Check if there is any intersection
  if (intersects.length > 0) {
      // Find the first intersected object
      const intersectedObject = intersects[0].object;

      // Check if the intersected object is not named 'Mesh'
      if (intersectedObject.name !== 'Mesh') {
          // Show the name of the intersected object
          document.getElementById('info').innerText = intersectedObject.name.replace(/_/g, ' ');
          document.getElementById('info').style.display = 'block';
      } else {
          // Hide the info window if the intersected object is named 'Mesh'
          document.getElementById('info').style.display = 'none';
      }
  } else {
      // Hide the info window if clicked outside the objects
      document.getElementById('info').style.display = 'none';
  }
}


function render() {

  renderer.render( scene, camera );

}

function animate() {
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}

// Start the 3D rendering
animate();