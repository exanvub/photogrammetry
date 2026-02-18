bl_info = {
    "name": "Landmark Registration",
    "author": "NVV",
    "version": (4, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Landmark Registration",
    "description": "Landmark registration",
    "category": "Object",
}

import bpy
import numpy as np
import math as mt
import mathutils as mu
import copy
import os
import blf
from bpy_extras import view3d_utils
import time #remove


# ─── Landmark Tracking System ───────────────────────────────────────────────

class LandmarkItem(bpy.types.PropertyGroup):
    """Represents a single landmark entry in the tracking list.
    Supports inline renaming in the UIList with live sync to the
    underlying landmarkDictionary stored on each object."""
    _is_syncing = False

    def on_name_update(self, context):
        if LandmarkItem._is_syncing:
            return

        old_name = self.internal_name
        new_name = self.name

        if old_name == new_name or not new_name.strip():
            if not new_name.strip():
                LandmarkItem._is_syncing = True
                self.name = old_name
                LandmarkItem._is_syncing = False
            return

        obj = bpy.data.objects.get(self.object_name)
        if obj and obj.get('landmarkDictionary'):
            landmark_dict = dict(obj['landmarkDictionary'])
            if old_name in landmark_dict:
                if new_name in landmark_dict:
                    # Name collision – revert
                    LandmarkItem._is_syncing = True
                    self.name = old_name
                    LandmarkItem._is_syncing = False
                    return
                vertex_idx = landmark_dict[old_name]
                del landmark_dict[old_name]
                landmark_dict[new_name] = vertex_idx
                obj['landmarkDictionary'] = landmark_dict
                self.internal_name = new_name

    name: bpy.props.StringProperty(name="Name", default="", update=on_name_update)
    internal_name: bpy.props.StringProperty(name="Internal Name", default="", options={'HIDDEN'})
    vertex_index: bpy.props.IntProperty(name="Vertex Index", default=-1, options={'HIDDEN'})
    object_name: bpy.props.StringProperty(name="Object", default="", options={'HIDDEN'})


class LANDMARK_UL_list(bpy.types.UIList):
    """UIList displaying all landmarks across objects."""

    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "name", text="", emboss=False, icon='PMARKER_ACT')
            sub = row.row()
            sub.alignment = 'RIGHT'
            sub.enabled = False
            sub.label(text=item.object_name)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text=item.name, icon='PMARKER_ACT')


def refresh_landmark_list(context):
    """Sync the UIList collection property with all objects' landmarkDictionary data."""
    scene = context.scene
    if not hasattr(scene, 'landmark_list'):
        return

    LandmarkItem._is_syncing = True
    prev_index = scene.landmark_list_index
    scene.landmark_list.clear()

    for obj in sorted(bpy.data.objects, key=lambda o: o.name):
        if obj.get('landmarkDictionary'):
            for lm_name, index in obj['landmarkDictionary'].items():
                item = scene.landmark_list.add()
                item.name = str(lm_name)
                item.internal_name = str(lm_name)
                item.vertex_index = int(index)
                item.object_name = obj.name

    if len(scene.landmark_list) > 0:
        scene.landmark_list_index = min(prev_index, len(scene.landmark_list) - 1)
    else:
        scene.landmark_list_index = 0

    LandmarkItem._is_syncing = False


# ─── Core Functions ─────────────────────────────────────────────────────────

def placeSeed(context, event):
    #define selected objects
    selectedObjects = context.selected_objects
    
    #define boundary conditions
    scene = context.scene
    region = context.region
    rv3d = context.region_data
    mouseCoordinates = event.mouse_region_x, event.mouse_region_y
    
    #convert cursor location and view direction
    viewVector = view3d_utils.region_2d_to_vector_3d(region, rv3d, mouseCoordinates)
    rayOrigin = view3d_utils.region_2d_to_origin_3d(region, rv3d, mouseCoordinates)
    rayTarget = rayOrigin + viewVector
    
    #ray cast procedure for selected objects
    successArray = []
    hitLocationArray = []
    distanceArray = []
    
    for object in selectedObjects:
        #convert to object space
        matrixInverted = object.matrix_world.inverted()
        rayOriginObject = matrixInverted @ rayOrigin
        rayTargetObject = matrixInverted @ rayTarget
        rayVectorObject = rayTargetObject - rayOriginObject
        
        #raycast procedure
        success, hitLocation, _, _ = object.ray_cast(rayOriginObject, rayVectorObject)
        
        #store success, location and distance
        successArray.append(success)
        hitLocationArray.append(hitLocation)
        distanceArray.append(np.linalg.norm(hitLocation - rayOriginObject))
        
    #if raycast successful on both objects, take the one closest to viewer
    if np.all(successArray):
        object = selectedObjects[np.argmin(distanceArray)]
        hitLocation = hitLocationArray[np.argmin(distanceArray)]
        
    #return nothing if no raycast hit
    elif not np.any(successArray):
        return None, None
    
    #in both other scenarios, only one object was hit
    else:
        object = selectedObjects[np.squeeze(np.where(successArray))]
        hitLocation = hitLocationArray[np.squeeze(np.where(successArray))]
    
    #build kd tree to get closest vertex
    tree = []
    tree = mu.kdtree.KDTree(len(object.data.vertices))
    for i, v in enumerate(object.data.vertices):
        tree.insert(v.co, i)
    tree.balance()
    
    _, seedIndex, _ = tree.find(hitLocation)
    return object, seedIndex

def drawTextCallback(context, dummy):
    #callback function for plotting seed positions
    
    for object in context.visible_objects:
        if object.get('landmarkDictionary') is not None:
            for landmark, index in object['landmarkDictionary'].items():
                vertLoc = object.matrix_world @ object.data.vertices[index].co
                vertLocOnScreen = view3d_utils.location_3d_to_region_2d(context.region, context.space_data.region_3d, vertLoc)
                blf.position(0, vertLocOnScreen[0] - 2, vertLocOnScreen[1] - 8, 0)
                blf.size(0, 20)
                blf.color(0, 1, 1, 0, 1)
                blf.draw(0, 'Â·' + landmark)
    return

class OBJECT_OT_placeLandmarks_operator(bpy.types.Operator):
    """Place landmarks on selected objects"""
    bl_idname = "object.placelandmarks"
    bl_label = "Place Landmarks"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        objects = len(context.selected_objects)
        return objects > 0
    
    def modal(self, context, event):
        #allow navigation
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        
        #confirm landmark placement
        elif event.type in {'RET', 'NUMPAD_ENTER'}:
            refresh_landmark_list(context)
            return {'FINISHED'}
        
        #cancel and delete landmarks
        elif event.type == 'ESC': 
            for object in context.selected_objects:
                if object.get('landmarkDictionary') is not None:
                    del object['landmarkDictionary']
            refresh_landmark_list(context)
            context.area.tag_redraw()
            return {'CANCELLED'}
        
        #place landmark
        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            bpy.types.SpaceView3D.draw_handler_add(drawTextCallback, (context, None), 'WINDOW', 'POST_PIXEL')
            
            object, seedIndex = placeSeed(context, event)
            
            #if landmark dictionary does not exists, make one
            if object is not None:
                if object.get('landmarkDictionary') is None:
                    object['landmarkDictionary'] = {}
            
            if seedIndex is None:  #no raycast hit
                self.report({'ERROR'}, "Cannot place landmark. Click on a selected object surface. Press ESC to cancel or ENTER to confirm.")
            else:
                if seedIndex not in object['landmarkDictionary'].values():
                    landmark = str(len(object['landmarkDictionary']) + 1)
                    object['landmarkDictionary'].update({landmark: seedIndex})
                    refresh_landmark_list(context)
                    self.report({'INFO'}, f"Placed landmark {landmark} on {object.name}")
                else:
                    self.report({'ERROR'}, f"Cannot place landmark on {object.name}. Another landmark is already at this position.")
            
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}
        return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

class OBJECT_OT_deleteLandmarks_operator(bpy.types.Operator):
    """Delete landmarks of selected objects"""
    bl_idname = "object.deletelandmarks"
    bl_label = "Delete Landmarks"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        objects = len(context.selected_objects)
        return objects > 0
            
    def execute(self, context):
        #delete dictionary
        deleted_count = 0
        for object in context.selected_objects:
            if object.get('landmarkDictionary') is not None:
                deleted_count += len(object['landmarkDictionary'])
                del object['landmarkDictionary']
        refresh_landmark_list(context)
        context.area.tag_redraw()
        
        if deleted_count > 0:
            self.report({'INFO'}, f"Deleted landmarks from {len(context.selected_objects)} objects")
        else:
            self.report({'INFO'}, "No landmarks found on selected objects")
        
        return {'FINISHED'}

class OBJECT_OT_deleteAllLandmarks_operator(bpy.types.Operator):
    """Delete ALL landmarks from ALL objects in the scene"""
    bl_idname = "object.deletealllandmarks"
    bl_label = "Delete All Landmarks"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return any(obj.get('landmarkDictionary') for obj in bpy.data.objects)
            
    def execute(self, context):
        #delete all landmark dictionaries
        deleted_objects = 0
        total_landmarks = 0
        for object in bpy.data.objects:
            if object.get('landmarkDictionary') is not None:
                total_landmarks += len(object['landmarkDictionary'])
                del object['landmarkDictionary']
                deleted_objects += 1
        refresh_landmark_list(context)
        context.area.tag_redraw()
        
        self.report({'INFO'}, f"Deleted {total_landmarks} landmarks from {deleted_objects} objects")
        return {'FINISHED'}

class OBJECT_OT_exportLandmarks_operator(bpy.types.Operator):
    """Export landmarks' coordinates to a file"""
    bl_idname = "object.export_landmarks"
    bl_label = "Export Landmarks"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        # Ensure at least one object in the scene has landmarks
        return any(obj.get('landmarkDictionary') for obj in bpy.data.objects)

    def execute(self, context):
        landmark_count = 0
        with open(self.filepath, 'w') as file:
            file.write("Object_Name,Landmark,X,Y,Z\n")
            # Export landmarks from all objects in the scene that have them
            for obj in bpy.data.objects:
                if obj.get('landmarkDictionary'):
                    for landmark, index in obj['landmarkDictionary'].items():
                        vertex_coord = obj.matrix_world @ obj.data.vertices[index].co
                        file.write(f"{obj.name},{landmark},{vertex_coord.x},{vertex_coord.y},{vertex_coord.z}\n")
                        landmark_count += 1
        
        self.report({'INFO'}, f"Exported {landmark_count} landmarks from {len([obj for obj in bpy.data.objects if obj.get('landmarkDictionary')])} objects to {self.filepath}")
        return {'FINISHED'}

    def invoke(self, context, event):
        # Set default file name
        default_filename = "landmarks.csv"
        self.filepath = bpy.path.abspath("//") + default_filename
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class OBJECT_OT_create_spheres_operator(bpy.types.Operator):
    """Create Ico spheres at landmark locations and store them in collections based on the mesh name"""
    bl_idname = "object.create_spheres"
    bl_label = "Create Spheres"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return any(obj.get('landmarkDictionary') for obj in bpy.data.objects)

    def execute(self, context):
        material_name = "LandmarkMaterial"

        # Create or retrieve the material
        if material_name in bpy.data.materials:
            landmark_material = bpy.data.materials[material_name]
        else:
            landmark_material = bpy.data.materials.new(name=material_name)
            landmark_material.diffuse_color = (1, 0, 0, 1)  # Red color (RGBA)

        sphere_count = 0
        # Process all objects in the scene that have landmarks
        for obj in bpy.data.objects:
            if obj.get('landmarkDictionary'):
                collection_name = f"Landmarks_{obj.name}"

                # Check if a collection exists for this object, otherwise create it
                if collection_name in bpy.data.collections:
                    landmark_collection = bpy.data.collections[collection_name]
                else:
                    landmark_collection = bpy.data.collections.new(collection_name)
                    bpy.context.scene.collection.children.link(landmark_collection)

                for landmark, index in obj['landmarkDictionary'].items():
                    vertex_coord = obj.matrix_world @ obj.data.vertices[index].co

                    # Create a new Ico sphere
                    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.02, location=vertex_coord)
                    sphere = bpy.context.object
                    sphere.name = f"Landmark_{landmark}_{obj.name}"
                    sphere_count += 1

                    # CLEAR PARENTING
                    sphere.parent = None

                    # Find the collection where the sphere was created
                    current_collection = sphere.users_collection[0] if sphere.users_collection else None

                    # Remove from the original collection (if found) and add to the specific object's collection
                    if current_collection:
                        current_collection.objects.unlink(sphere)

                    landmark_collection.objects.link(sphere)  # Add to the correct collection

                    # Assign the material
                    if len(sphere.data.materials) == 0:
                        sphere.data.materials.append(landmark_material)
                    else:
                        sphere.data.materials[0] = landmark_material  # Replace existing material

        self.report({'INFO'}, f"Created {sphere_count} spheres and sorted into collections based on mesh names.")
        return {'FINISHED'}

# ─── Landmark List Management Operators ─────────────────────────────────────

class LANDMARK_OT_refresh_list(bpy.types.Operator):
    """Refresh the landmark list from all objects in the scene"""
    bl_idname = "landmark.refresh_list"
    bl_label = "Refresh List"

    def execute(self, context):
        refresh_landmark_list(context)
        self.report({'INFO'}, "Landmark list refreshed")
        return {'FINISHED'}


class LANDMARK_OT_delete_single(bpy.types.Operator):
    """Delete the selected landmark from the list and the object"""
    bl_idname = "landmark.delete_single"
    bl_label = "Delete Landmark"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        return (hasattr(scene, 'landmark_list') and
                len(scene.landmark_list) > 0 and
                0 <= scene.landmark_list_index < len(scene.landmark_list))

    def execute(self, context):
        scene = context.scene
        idx = scene.landmark_list_index
        item = scene.landmark_list[idx]

        lm_name = item.internal_name
        obj_name = item.object_name

        # Remove from the object's landmark dictionary
        obj = bpy.data.objects.get(obj_name)
        if obj and obj.get('landmarkDictionary'):
            landmark_dict = dict(obj['landmarkDictionary'])
            if lm_name in landmark_dict:
                del landmark_dict[lm_name]
                if landmark_dict:
                    obj['landmarkDictionary'] = landmark_dict
                else:
                    del obj['landmarkDictionary']

        # Remove from UIList
        scene.landmark_list.remove(idx)
        scene.landmark_list_index = min(max(0, idx - 1),
                                        max(0, len(scene.landmark_list) - 1))

        context.area.tag_redraw()
        self.report({'INFO'}, f"Deleted landmark '{lm_name}' from {obj_name}")
        return {'FINISHED'}


class LANDMARK_OT_rename(bpy.types.Operator):
    """Rename the selected landmark via a dialog"""
    bl_idname = "landmark.rename"
    bl_label = "Rename Landmark"
    bl_options = {'REGISTER', 'UNDO'}

    new_name: bpy.props.StringProperty(name="New Name", default="")

    @classmethod
    def poll(cls, context):
        scene = context.scene
        return (hasattr(scene, 'landmark_list') and
                len(scene.landmark_list) > 0 and
                0 <= scene.landmark_list_index < len(scene.landmark_list))

    def invoke(self, context, event):
        scene = context.scene
        item = scene.landmark_list[scene.landmark_list_index]
        self.new_name = item.name
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, "new_name")

    def execute(self, context):
        scene = context.scene
        idx = scene.landmark_list_index
        item = scene.landmark_list[idx]
        old_name = item.internal_name

        if not self.new_name.strip():
            self.report({'ERROR'}, "Name cannot be empty")
            return {'CANCELLED'}

        if self.new_name == old_name:
            return {'CANCELLED'}

        obj = bpy.data.objects.get(item.object_name)
        if obj and obj.get('landmarkDictionary'):
            landmark_dict = dict(obj['landmarkDictionary'])
            if old_name in landmark_dict:
                if self.new_name in landmark_dict:
                    self.report({'ERROR'},
                                f"Landmark '{self.new_name}' already exists on {obj.name}")
                    return {'CANCELLED'}
                vertex_idx = landmark_dict[old_name]
                del landmark_dict[old_name]
                landmark_dict[self.new_name] = vertex_idx
                obj['landmarkDictionary'] = landmark_dict

        LandmarkItem._is_syncing = True
        item.name = self.new_name
        item.internal_name = self.new_name
        LandmarkItem._is_syncing = False

        context.area.tag_redraw()
        self.report({'INFO'}, f"Renamed '{old_name}' to '{self.new_name}'")
        return {'FINISHED'}


class LANDMARK_OT_jump_to(bpy.types.Operator):
    """Center the 3D viewport on the selected landmark"""
    bl_idname = "landmark.jump_to"
    bl_label = "Jump to Landmark"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        return (hasattr(scene, 'landmark_list') and
                len(scene.landmark_list) > 0 and
                0 <= scene.landmark_list_index < len(scene.landmark_list))

    def execute(self, context):
        scene = context.scene
        item = scene.landmark_list[scene.landmark_list_index]

        obj = bpy.data.objects.get(item.object_name)
        if not obj or not obj.data or item.vertex_index >= len(obj.data.vertices):
            self.report({'ERROR'},
                        f"Could not locate landmark vertex on '{item.object_name}'")
            return {'CANCELLED'}

        vertex_coord = obj.matrix_world @ obj.data.vertices[item.vertex_index].co
        context.scene.cursor.location = vertex_coord

        # Center view on cursor (context override for Blender 4.0+)
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        with context.temp_override(area=area, region=region):
                            bpy.ops.view3d.view_center_cursor()
                        break
                break

        self.report({'INFO'}, f"Centered on '{item.name}' ({item.object_name})")
        return {'FINISHED'}


# ─── UI Panel ───────────────────────────────────────────────────────────────

class OBJECT_Landmark_panel(bpy.types.Panel):
    bl_category = "Landmark Registration"
    bl_label = "Landmark Registration"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # ── Status ──
        objects_with_landmarks = [obj for obj in bpy.data.objects if obj.get('landmarkDictionary')]
        total_landmarks = sum(len(obj['landmarkDictionary']) for obj in objects_with_landmarks)

        if objects_with_landmarks:
            layout.label(text=f"Landmarks: {total_landmarks} on {len(objects_with_landmarks)} object(s)",
                         icon='INFO')
        else:
            layout.label(text="No landmarks placed", icon='INFO')

        selected_count = len(context.selected_objects)
        if selected_count > 0:
            layout.label(text=f"Selected: {selected_count} object(s)",
                         icon='RESTRICT_SELECT_OFF')
        else:
            layout.label(text="No objects selected", icon='RESTRICT_SELECT_ON')

        layout.separator()

        # ── Place Landmarks ──
        layout.operator("object.placelandmarks", text="Place Landmarks", icon='PMARKER_ACT')

        layout.separator()

        # ── Landmark List ──
        header = layout.row()
        header.label(text="Landmark List", icon='OUTLINER_OB_POINTCLOUD')
        header.operator("landmark.refresh_list", text="", icon='FILE_REFRESH')

        row = layout.row()
        row.template_list("LANDMARK_UL_list", "", scene, "landmark_list",
                          scene, "landmark_list_index", rows=5)

        col = row.column(align=True)
        col.operator("landmark.delete_single", icon='REMOVE', text="")
        col.separator()
        col.operator("landmark.rename", icon='SORTALPHA', text="")
        col.operator("landmark.jump_to", icon='VIEWZOOM', text="")

        # ── Selected Landmark Details ──
        if (hasattr(scene, 'landmark_list') and
            len(scene.landmark_list) > 0 and
            0 <= scene.landmark_list_index < len(scene.landmark_list)):
            item = scene.landmark_list[scene.landmark_list_index]
            box = layout.box()
            row = box.row()
            row.label(text=f"Object: {item.object_name}", icon='OBJECT_DATA')
            row.label(text=f"Vertex: {item.vertex_index}")
            obj = bpy.data.objects.get(item.object_name)
            if obj and obj.data and item.vertex_index < len(obj.data.vertices):
                co = obj.matrix_world @ obj.data.vertices[item.vertex_index].co
                box.label(text=f"World Pos: ({co.x:.4f}, {co.y:.4f}, {co.z:.4f})")

        layout.separator()

        # ── Bulk Operations ──
        layout.label(text="Bulk Operations", icon='TRASH')
        layout.operator("object.deletelandmarks", text="Delete Selected Object Landmarks", icon='X')
        layout.operator("object.deletealllandmarks", text="Delete ALL Landmarks", icon='CANCEL')

        layout.separator()

        # ── Export & Visualization ──
        layout.label(text="Export & Visualization", icon='EXPORT')
        layout.operator("object.export_landmarks", text="Export All Landmarks", icon='FILE')
        layout.operator("object.create_spheres", text="Create Landmark Spheres", icon='MESH_UVSPHERE')

class globalVars():
    pass

classes = (
    LandmarkItem,
    LANDMARK_UL_list,
    OBJECT_OT_placeLandmarks_operator,
    OBJECT_OT_deleteLandmarks_operator,
    OBJECT_OT_deleteAllLandmarks_operator,
    OBJECT_OT_exportLandmarks_operator,
    OBJECT_OT_create_spheres_operator,
    LANDMARK_OT_refresh_list,
    LANDMARK_OT_delete_single,
    LANDMARK_OT_rename,
    LANDMARK_OT_jump_to,
    OBJECT_Landmark_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.landmark_list = bpy.props.CollectionProperty(type=LandmarkItem)
    bpy.types.Scene.landmark_list_index = bpy.props.IntProperty(name="Active Landmark", default=0)


def unregister():
    del bpy.types.Scene.landmark_list_index
    del bpy.types.Scene.landmark_list
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
if __name__ == "__main__":
    register()



