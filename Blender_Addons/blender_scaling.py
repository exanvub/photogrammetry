bl_info = {
    "name": "3D Model Scaling",
    "author": "NVV",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Model Scaling",
    "description": "Scale photogrammetry models to real-world dimensions using point-pair measurements",
    "category": "Object",
}

import bpy
import numpy as np
import mathutils as mu
import blf
from bpy_extras import view3d_utils


# ─── Helpers ──────────────────────────────────────────────────────────────────

def raycast_vertex(context, event):
    """Raycast from mouse position onto the selected mesh and return
    (object, vertex_index) snapped to the nearest vertex, or (None, None)."""
    selected_objects = context.selected_objects
    scene = context.scene
    region = context.region
    rv3d = context.region_data
    mouse_co = (event.mouse_region_x, event.mouse_region_y)

    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, mouse_co)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, mouse_co)
    ray_target = ray_origin + view_vector

    success_arr = []
    hit_loc_arr = []
    dist_arr = []

    for obj in selected_objects:
        mat_inv = obj.matrix_world.inverted()
        ray_origin_obj = mat_inv @ ray_origin
        ray_target_obj = mat_inv @ ray_target
        ray_dir_obj = ray_target_obj - ray_origin_obj

        success, hit_loc, _, _ = obj.ray_cast(ray_origin_obj, ray_dir_obj)
        success_arr.append(success)
        hit_loc_arr.append(hit_loc)
        dist_arr.append(np.linalg.norm(hit_loc - ray_origin_obj))

    if np.all(success_arr):
        obj = selected_objects[np.argmin(dist_arr)]
        hit_loc = hit_loc_arr[np.argmin(dist_arr)]
    elif not np.any(success_arr):
        return None, None
    else:
        idx = int(np.squeeze(np.where(success_arr)))
        obj = selected_objects[idx]
        hit_loc = hit_loc_arr[idx]

    # Snap to nearest vertex via KD-tree
    tree = mu.kdtree.KDTree(len(obj.data.vertices))
    for i, v in enumerate(obj.data.vertices):
        tree.insert(v.co, i)
    tree.balance()

    _, vert_idx, _ = tree.find(hit_loc)
    return obj, vert_idx


def get_vertex_world_co(obj, vert_idx):
    """Return the world-space coordinate of a vertex."""
    return obj.matrix_world @ obj.data.vertices[vert_idx].co


# ─── Property Groups ─────────────────────────────────────────────────────────

class ScalingMeasurement(bpy.types.PropertyGroup):
    """A single point-pair measurement: two vertices + a real-world distance."""

    def _update(self, context):
        """Recalculate distances when real-world value changes."""
        recalculate_scaling(context)

    # Point A
    object_a: bpy.props.StringProperty(name="Object A")
    vertex_a: bpy.props.IntProperty(name="Vertex A", default=-1)
    # Point B
    object_b: bpy.props.StringProperty(name="Object B")
    vertex_b: bpy.props.IntProperty(name="Vertex B", default=-1)

    model_distance: bpy.props.FloatProperty(
        name="Model Distance", default=0.0, precision=6,
        description="Euclidean distance between the two points in model/Blender units")
    real_distance: bpy.props.FloatProperty(
        name="Real Distance (mm)", default=0.0, precision=4, min=0.0,
        description="Corresponding real-world distance in millimetres",
        update=_update)

    label: bpy.props.StringProperty(name="Label", default="")
    point_count: bpy.props.IntProperty(
        name="Points Placed", default=0, min=0, max=2,
        description="How many of the two points have been placed so far")


class SCALING_UL_measurements(bpy.types.UIList):
    """UIList for the measurement pairs."""

    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            # Status icon
            if item.point_count < 2:
                ic = 'RADIOBUT_OFF'
            elif item.real_distance <= 0:
                ic = 'ERROR'
            else:
                ic = 'CHECKMARK'

            row.label(text="", icon=ic)
            sub = row.row(align=True)
            sub.prop(item, "label", text="", emboss=False)

            sub2 = row.row(align=True)
            sub2.alignment = 'RIGHT'
            if item.point_count == 2:
                sub2.label(text=f"{item.model_distance:.4f}")
            else:
                sub2.label(text=f"{item.point_count}/2 pts")
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text=item.label, icon='ARROW_LEFTRIGHT')


# ─── Viewport Drawing ────────────────────────────────────────────────────────

_draw_handle = None


def _draw_scaling_overlay(context, _dummy):
    """Draw labels and lines for measurement pairs in the viewport."""
    scene = context.scene
    if not hasattr(scene, 'scaling_measurements'):
        return

    region = context.region
    rv3d = context.space_data.region_3d

    for meas in scene.scaling_measurements:
        pts_screen = []
        for attr_obj, attr_v in [("object_a", "vertex_a"), ("object_b", "vertex_b")]:
            obj_name = getattr(meas, attr_obj)
            vert_idx = getattr(meas, attr_v)
            obj = bpy.data.objects.get(obj_name)
            if obj and obj.data and 0 <= vert_idx < len(obj.data.vertices):
                world_co = get_vertex_world_co(obj, vert_idx)
                screen_co = view3d_utils.location_3d_to_region_2d(region, rv3d, world_co)
                if screen_co:
                    pts_screen.append(screen_co)

        # Draw point labels
        for i, sc in enumerate(pts_screen):
            blf.position(0, sc[0] + 6, sc[1] - 4, 0)
            blf.size(0, 16)
            blf.color(0, 0.2, 1.0, 0.2, 1.0)
            blf.draw(0, f"{'A' if i == 0 else 'B'}")

        # Draw distance label at midpoint
        if len(pts_screen) == 2:
            mid = ((pts_screen[0][0] + pts_screen[1][0]) / 2,
                   (pts_screen[0][1] + pts_screen[1][1]) / 2)
            blf.position(0, mid[0] + 6, mid[1] + 6, 0)
            blf.size(0, 14)
            blf.color(0, 1.0, 1.0, 0.0, 1.0)
            blf.draw(0, f"{meas.label}: {meas.model_distance:.4f}")


def ensure_draw_handler(context):
    global _draw_handle
    if _draw_handle is None:
        _draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            _draw_scaling_overlay, (context, None), 'WINDOW', 'POST_PIXEL')


def remove_draw_handler():
    global _draw_handle
    if _draw_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_draw_handle, 'WINDOW')
        _draw_handle = None


# ─── Scaling Calculation ─────────────────────────────────────────────────────

def recalculate_scaling(context):
    """Recalculate model distances and the average scaling factor."""
    scene = context.scene
    model_dists = []
    real_dists = []

    for meas in scene.scaling_measurements:
        if meas.point_count < 2:
            continue
        obj_a = bpy.data.objects.get(meas.object_a)
        obj_b = bpy.data.objects.get(meas.object_b)
        if not obj_a or not obj_b:
            continue
        if meas.vertex_a < 0 or meas.vertex_b < 0:
            continue

        co_a = get_vertex_world_co(obj_a, meas.vertex_a)
        co_b = get_vertex_world_co(obj_b, meas.vertex_b)
        dist = (co_a - co_b).length
        meas.model_distance = dist

        if meas.real_distance > 0 and dist > 0:
            model_dists.append(dist)
            real_dists.append(meas.real_distance)

    if model_dists:
        factors = [r / m for m, r in zip(model_dists, real_dists)]
        scene.scaling_factor = float(np.mean(factors))
        scene.scaling_factor_std = float(np.std(factors)) if len(factors) > 1 else 0.0
        scene.scaling_valid_pairs = len(factors)
    else:
        scene.scaling_factor = 0.0
        scene.scaling_factor_std = 0.0
        scene.scaling_valid_pairs = 0


# ─── Operators ────────────────────────────────────────────────────────────────

class SCALING_OT_add_measurement(bpy.types.Operator):
    """Add a new measurement pair and enter point-picking mode"""
    bl_idname = "scaling.add_measurement"
    bl_label = "Add Measurement"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def modal(self, context, event):
        scene = context.scene
        idx = scene.scaling_measurements_index
        meas = scene.scaling_measurements[idx]

        # Allow viewport navigation
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}

        # Cancel
        if event.type == 'ESC':
            # Remove the incomplete measurement
            scene.scaling_measurements.remove(idx)
            scene.scaling_measurements_index = max(0, len(scene.scaling_measurements) - 1)
            self.report({'INFO'}, "Measurement cancelled")
            context.area.tag_redraw()
            return {'CANCELLED'}

        # Place a point
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            obj, vert_idx = raycast_vertex(context, event)
            if obj is None:
                self.report({'WARNING'}, "Click on a selected object surface")
                return {'RUNNING_MODAL'}

            if meas.point_count == 0:
                meas.object_a = obj.name
                meas.vertex_a = vert_idx
                meas.point_count = 1
                self.report({'INFO'}, f"Point A placed on {obj.name} (vertex {vert_idx}). Now click Point B.")
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}

            elif meas.point_count == 1:
                meas.object_b = obj.name
                meas.vertex_b = vert_idx
                meas.point_count = 2

                # Calculate model distance
                co_a = get_vertex_world_co(
                    bpy.data.objects[meas.object_a], meas.vertex_a)
                co_b = get_vertex_world_co(obj, vert_idx)
                meas.model_distance = (co_a - co_b).length

                recalculate_scaling(context)
                self.report({'INFO'},
                            f"Point B placed. Model distance: {meas.model_distance:.6f}. "
                            f"Enter real-world distance in the panel.")
                context.area.tag_redraw()
                return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        scene = context.scene
        ensure_draw_handler(context)

        # Create new measurement entry
        meas = scene.scaling_measurements.add()
        idx = len(scene.scaling_measurements) - 1
        meas.label = f"M{idx + 1}"
        meas.point_count = 0
        scene.scaling_measurements_index = idx

        self.report({'INFO'}, "Click to place Point A on the model surface")
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class SCALING_OT_pick_points(bpy.types.Operator):
    """Re-pick the two points for the active measurement"""
    bl_idname = "scaling.pick_points"
    bl_label = "Re-pick Points"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        return (len(context.selected_objects) > 0 and
                len(scene.scaling_measurements) > 0 and
                0 <= scene.scaling_measurements_index < len(scene.scaling_measurements))

    def modal(self, context, event):
        scene = context.scene
        meas = scene.scaling_measurements[scene.scaling_measurements_index]

        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}

        if event.type == 'ESC':
            # Restore old values
            meas.object_a = self._old_obj_a
            meas.vertex_a = self._old_vert_a
            meas.object_b = self._old_obj_b
            meas.vertex_b = self._old_vert_b
            meas.point_count = self._old_count
            meas.model_distance = self._old_dist
            recalculate_scaling(context)
            self.report({'INFO'}, "Re-pick cancelled")
            context.area.tag_redraw()
            return {'CANCELLED'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            obj, vert_idx = raycast_vertex(context, event)
            if obj is None:
                self.report({'WARNING'}, "Click on a selected object surface")
                return {'RUNNING_MODAL'}

            if meas.point_count == 0:
                meas.object_a = obj.name
                meas.vertex_a = vert_idx
                meas.point_count = 1
                self.report({'INFO'}, "Point A placed. Click Point B.")
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}

            elif meas.point_count == 1:
                meas.object_b = obj.name
                meas.vertex_b = vert_idx
                meas.point_count = 2
                co_a = get_vertex_world_co(
                    bpy.data.objects[meas.object_a], meas.vertex_a)
                co_b = get_vertex_world_co(obj, vert_idx)
                meas.model_distance = (co_a - co_b).length
                recalculate_scaling(context)
                self.report({'INFO'},
                            f"Points re-picked. Model distance: {meas.model_distance:.6f}")
                context.area.tag_redraw()
                return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        scene = context.scene
        meas = scene.scaling_measurements[scene.scaling_measurements_index]
        ensure_draw_handler(context)

        # Save old state for cancel
        self._old_obj_a = meas.object_a
        self._old_vert_a = meas.vertex_a
        self._old_obj_b = meas.object_b
        self._old_vert_b = meas.vertex_b
        self._old_count = meas.point_count
        self._old_dist = meas.model_distance

        # Reset for re-picking
        meas.point_count = 0
        meas.vertex_a = -1
        meas.vertex_b = -1

        self.report({'INFO'}, "Click to place Point A")
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class SCALING_OT_remove_measurement(bpy.types.Operator):
    """Remove the selected measurement pair"""
    bl_idname = "scaling.remove_measurement"
    bl_label = "Remove Measurement"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        return (len(scene.scaling_measurements) > 0 and
                0 <= scene.scaling_measurements_index < len(scene.scaling_measurements))

    def execute(self, context):
        scene = context.scene
        idx = scene.scaling_measurements_index
        label = scene.scaling_measurements[idx].label
        scene.scaling_measurements.remove(idx)
        scene.scaling_measurements_index = min(
            max(0, idx - 1), max(0, len(scene.scaling_measurements) - 1))
        recalculate_scaling(context)
        context.area.tag_redraw()
        self.report({'INFO'}, f"Removed measurement '{label}'")
        return {'FINISHED'}


class SCALING_OT_clear_all(bpy.types.Operator):
    """Remove all measurement pairs"""
    bl_idname = "scaling.clear_all"
    bl_label = "Clear All Measurements"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(context.scene.scaling_measurements) > 0

    def execute(self, context):
        context.scene.scaling_measurements.clear()
        context.scene.scaling_measurements_index = 0
        context.scene.scaling_factor = 0.0
        context.scene.scaling_factor_std = 0.0
        context.scene.scaling_valid_pairs = 0
        context.area.tag_redraw()
        self.report({'INFO'}, "All measurements cleared")
        return {'FINISHED'}


class SCALING_OT_apply_scaling(bpy.types.Operator):
    """Apply the computed scaling factor to the selected objects"""
    bl_idname = "scaling.apply"
    bl_label = "Apply Scaling"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.scene.scaling_factor > 0 and
                len(context.selected_objects) > 0)

    def execute(self, context):
        scene = context.scene
        sf = scene.scaling_factor

        for obj in context.selected_objects:
            obj.scale *= sf

        # After scaling, recalculate model distances (they've changed)
        # Apply scale to make it permanent first
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        recalculate_scaling(context)
        context.area.tag_redraw()

        self.report({'INFO'},
                    f"Applied scaling factor {sf:.6f} to "
                    f"{len(context.selected_objects)} object(s)")
        return {'FINISHED'}


class SCALING_OT_apply_scaling_no_apply(bpy.types.Operator):
    """Apply the scaling factor without applying the transform (keeps scale editable)"""
    bl_idname = "scaling.apply_no_freeze"
    bl_label = "Apply Scaling (Keep Transform)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.scene.scaling_factor > 0 and
                len(context.selected_objects) > 0)

    def execute(self, context):
        scene = context.scene
        sf = scene.scaling_factor

        for obj in context.selected_objects:
            obj.scale *= sf

        recalculate_scaling(context)
        context.area.tag_redraw()

        self.report({'INFO'},
                    f"Scaled by {sf:.6f} (transform not applied)")
        return {'FINISHED'}


class SCALING_OT_recalculate(bpy.types.Operator):
    """Recalculate all model distances and the scaling factor"""
    bl_idname = "scaling.recalculate"
    bl_label = "Recalculate"

    def execute(self, context):
        recalculate_scaling(context)
        context.area.tag_redraw()
        self.report({'INFO'}, "Recalculated scaling factor")
        return {'FINISHED'}


class SCALING_OT_toggle_overlay(bpy.types.Operator):
    """Toggle the viewport measurement overlay"""
    bl_idname = "scaling.toggle_overlay"
    bl_label = "Toggle Overlay"

    def execute(self, context):
        global _draw_handle
        if _draw_handle is None:
            ensure_draw_handler(context)
            self.report({'INFO'}, "Overlay enabled")
        else:
            remove_draw_handler()
            context.area.tag_redraw()
            self.report({'INFO'}, "Overlay disabled")
        return {'FINISHED'}


# ─── UI Panel ─────────────────────────────────────────────────────────────────

class SCALING_PT_main_panel(bpy.types.Panel):
    bl_category = "Model Scaling"
    bl_label = "3D Model Scaling"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # ── Status ──
        n_meas = len(scene.scaling_measurements)
        selected = len(context.selected_objects)

        if selected > 0:
            layout.label(text=f"Selected: {selected} object(s)",
                         icon='RESTRICT_SELECT_OFF')
        else:
            layout.label(text="No objects selected", icon='RESTRICT_SELECT_ON')

        layout.separator()

        # ── Add measurement ──
        layout.operator("scaling.add_measurement",
                        text="Add Measurement Pair", icon='ADD')

        layout.separator()

        # ── Measurement list ──
        header = layout.row()
        header.label(text="Measurements", icon='ARROW_LEFTRIGHT')
        header.operator("scaling.toggle_overlay", text="", icon='OVERLAY')
        header.operator("scaling.recalculate", text="", icon='FILE_REFRESH')

        row = layout.row()
        row.template_list("SCALING_UL_measurements", "", scene,
                          "scaling_measurements", scene,
                          "scaling_measurements_index", rows=4)

        col = row.column(align=True)
        col.operator("scaling.remove_measurement", icon='REMOVE', text="")
        col.separator()
        col.operator("scaling.pick_points", icon='EYEDROPPER', text="")

        # ── Selected measurement details ──
        if (n_meas > 0 and
                0 <= scene.scaling_measurements_index < n_meas):
            meas = scene.scaling_measurements[scene.scaling_measurements_index]
            box = layout.box()

            row = box.row()
            row.prop(meas, "label", text="Label")

            if meas.point_count == 2:
                row = box.row(align=True)
                row.label(text=f"A: {meas.object_a} v{meas.vertex_a}",
                          icon='PMARKER')
                row.label(text=f"B: {meas.object_b} v{meas.vertex_b}",
                          icon='PMARKER')

                box.label(text=f"Model Distance: {meas.model_distance:.6f}",
                          icon='DRIVER_DISTANCE')

                box.prop(meas, "real_distance",
                         text="Real-World Distance (mm)")
            else:
                box.label(text=f"Points placed: {meas.point_count} / 2",
                          icon='RADIOBUT_OFF')

        layout.separator()

        # ── Results ──
        results_box = layout.box()
        results_box.label(text="Scaling Results", icon='VIEWZOOM')

        row = results_box.row()
        row.label(text=f"Valid pairs: {scene.scaling_valid_pairs} / {n_meas}")

        if scene.scaling_factor > 0:
            results_box.label(
                text=f"Scaling Factor: {scene.scaling_factor:.6f}",
                icon='FULLSCREEN_ENTER')
            if scene.scaling_factor_std > 0:
                results_box.label(
                    text=f"Std Dev: {scene.scaling_factor_std:.6f}",
                    icon='INFO')
        else:
            results_box.label(text="No valid scaling factor yet",
                              icon='ERROR')

        layout.separator()

        # ── Apply buttons ──
        col = layout.column(align=True)
        col.operator("scaling.apply",
                     text="Apply Scaling & Freeze Transform",
                     icon='CHECKMARK')
        col.operator("scaling.apply_no_freeze",
                     text="Apply Scaling (Keep Transform)",
                     icon='CON_SIZELIKE')

        layout.separator()
        layout.operator("scaling.clear_all",
                        text="Clear All Measurements", icon='CANCEL')


# ─── Registration ─────────────────────────────────────────────────────────────

classes = (
    ScalingMeasurement,
    SCALING_UL_measurements,
    SCALING_OT_add_measurement,
    SCALING_OT_pick_points,
    SCALING_OT_remove_measurement,
    SCALING_OT_clear_all,
    SCALING_OT_apply_scaling,
    SCALING_OT_apply_scaling_no_apply,
    SCALING_OT_recalculate,
    SCALING_OT_toggle_overlay,
    SCALING_PT_main_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.scaling_measurements = bpy.props.CollectionProperty(
        type=ScalingMeasurement)
    bpy.types.Scene.scaling_measurements_index = bpy.props.IntProperty(
        name="Active Measurement", default=0)
    bpy.types.Scene.scaling_factor = bpy.props.FloatProperty(
        name="Scaling Factor", default=0.0, precision=6)
    bpy.types.Scene.scaling_factor_std = bpy.props.FloatProperty(
        name="Scaling Factor Std Dev", default=0.0, precision=6)
    bpy.types.Scene.scaling_valid_pairs = bpy.props.IntProperty(
        name="Valid Pairs", default=0)


def unregister():
    remove_draw_handler()

    del bpy.types.Scene.scaling_valid_pairs
    del bpy.types.Scene.scaling_factor_std
    del bpy.types.Scene.scaling_factor
    del bpy.types.Scene.scaling_measurements_index
    del bpy.types.Scene.scaling_measurements

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
