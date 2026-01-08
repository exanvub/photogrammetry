import bpy
import sys
import addon_utils

def enable_usd_import():
    """Ensure the USD import/export add-on is enabled"""
    addon_utils.enable('io_import_usd', default_set=True)

def convert_usdz_to_ply(input_path, output_path):
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Import USDZ file
    bpy.ops.wm.usd_import(
        filepath=input_path,
        import_materials=False,
        import_cameras=False,
        import_lights=False
    )

    # Select all mesh objects
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    if not meshes:
        raise Exception("No mesh objects found in USDZ file")

    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]

    # Apply transformations
    bpy.ops.object.transform_apply(
        location=True,
        rotation=True,
        scale=True
    )

    # Join all meshes into one object
    if len(meshes) > 1:
        bpy.ops.object.join()

    # Export as PLY
    bpy.ops.export_mesh.ply(
        filepath=output_path,
        use_selection=True,
        include_normals=True,
        include_uvs=False,
        include_colors=False
    )

if __name__ == "__main__":
    # Enable required add-on
    enable_usd_import()

    # Parse command line arguments
    try:
        args = sys.argv[sys.argv.index("--") + 1:]
        input_usdz = args[0]
        output_ply = args[1]
    except:
        print("Usage: blender --background --python script.py -- input.usdz output.ply")
        sys.exit(1)

    # Perform conversion
    convert_usdz_to_ply(input_usdz, output_ply)
    print(f"Successfully converted {input_usdz} to {output_ply}")