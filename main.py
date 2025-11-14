import open3d as o3d
import numpy as np
import copy
import os

def visualize_step(geometries, title, step_number):
    """Функция для пошаговой визуализации"""
    print(f"\n{step_number}. {title}")
    print("➡️ Закройте это окно чтобы продолжить...")
    
    if not isinstance(geometries, list):
        geometries = [geometries]
    
    o3d.visualization.draw_geometries(geometries, window_name=f"Step {step_number}: {title}")

def main():
    print("=" * 70)
    print("3D MODEL PROCESSING - ASSIGNMENT #5")
    print("=" * 70)
    
    # Step 1: Loading and Visualization
    mesh_path = r"C:\Users\Med36\Downloads\skull.obj"
    
    print(f"Загружаем модель: {os.path.basename(mesh_path)}")
    mesh = o3d.io.read_triangle_mesh(mesh_path)
    
    # Проверка загрузки
    if len(mesh.vertices) == 0:
        print("❌ Модель не загрузилась! Создаем альтернативную...")
        # Создаем простую модель для демонстрации
        mesh = o3d.geometry.TriangleMesh.create_sphere()
        mesh.compute_vertex_normals()
    else:
        print(f"✅ Модель загружена успешно!")
    
    # Вычисляем нормали если их нет
    if not mesh.has_vertex_normals():
        mesh.compute_vertex_normals()
    if not mesh.has_triangle_normals():
        mesh.compute_triangle_normals()
    
    visualize_step(mesh, "ORIGINAL MODEL", 1)
    
    print(f"Number of vertices: {len(mesh.vertices)}")
    print(f"Number of triangles: {len(mesh.triangles)}")
    print(f"Has vertex colors: {mesh.has_vertex_colors()}")
    print(f"Has vertex normals: {mesh.has_vertex_normals()}")
    
    # Step 2: Conversion to Point Cloud
    point_cloud = mesh.sample_points_poisson_disk(number_of_points=3000)
    visualize_step(point_cloud, "POINT CLOUD", 2)
    
    print(f"Number of points: {len(point_cloud.points)}")
    print(f"Has colors: {point_cloud.has_colors()}")
    
    # Step 3: Surface Reconstruction
    try:
        reconstructed_mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
            point_cloud, depth=8)
        
        # Remove artifacts
        if len(densities) > 0:
            density_threshold = np.quantile(densities, 0.02)
            vertices_to_remove = densities < density_threshold
            reconstructed_mesh.remove_vertices_by_mask(vertices_to_remove)
        
        visualize_step(reconstructed_mesh, "SURFACE RECONSTRUCTION", 3)
        
        print(f"Number of vertices: {len(reconstructed_mesh.vertices)}")
        print(f"Number of triangles: {len(reconstructed_mesh.triangles)}")
        print(f"Has vertex colors: {reconstructed_mesh.has_vertex_colors()}")
        
    except Exception as e:
        print(f"Reconstruction failed: {e}")
        print("Using original mesh for reconstruction step")
        reconstructed_mesh = copy.deepcopy(mesh)
    
    # Step 4: Voxelization
    # Автоматический расчет размера вокселя
    bbox = point_cloud.get_axis_aligned_bounding_box()
    bbox_size = bbox.get_extent()
    voxel_size = max(bbox_size) / 25  # Автоматический расчет
    
    voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(point_cloud, 
                                                               voxel_size=voxel_size)
    visualize_step(voxel_grid, "VOXEL GRID", 4)
    
    print(f"Voxel size: {voxel_size:.4f}")
    print(f"Number of voxels: {len(voxel_grid.get_voxels())}")
    
    # Step 5: Adding a Plane (ИЗМЕНЕНО)
    # Get the bounding box to position the plane properly
    bbox = mesh.get_axis_aligned_bounding_box()
    bbox_min = bbox.get_min_bound()
    bbox_max = bbox.get_max_bound()
    
    # Create a vertical plane that cuts through the middle of the object
    plane_height = (bbox_max[1] - bbox_min[1]) * 1.5  # Tall enough to cover the object
    plane_depth = (bbox_max[2] - bbox_min[2]) * 1.5   # Deep enough to cover the object
    plane = o3d.geometry.TriangleMesh.create_box(width=0.02, height=plane_height, depth=plane_depth)
    
    # Position the plane through the center of the object (cutting along X-axis)
    plane_center = [(bbox_min[0] + bbox_max[0]) / 2,  # Center X (cutting plane)
                   (bbox_min[1] + bbox_max[1]) / 2,   # Center Y
                   (bbox_min[2] + bbox_max[2]) / 2]   # Center Z
    
    plane.translate([plane_center[0] - 0.01,  # Center the thin plane on X
                    plane_center[1] - plane_height/2, 
                    plane_center[2] - plane_depth/2])
    
    plane.paint_uniform_color([0.3, 0.7, 0.3])  # Green color
    
    # Create a copy of the original mesh for display with plane
    mesh_with_plane = copy.deepcopy(mesh)
    mesh_with_plane.paint_uniform_color([0.7, 0.7, 0.7])
    
    visualize_step([mesh_with_plane, plane], "OBJECT WITH CUTTING PLANE", 5)
    
    print("Created a vertical cutting plane through the middle of the skull")
    print(f"Plane position: x = {plane_center[0]:.2f} (cutting plane)")
    print(f"Plane dimensions: 0.02 x {plane_height:.2f} x {plane_depth:.2f}")
    
    # Step 6: Surface Clipping (ИЗМЕНЕНО)
    # Create a copy for clipping
    mesh_to_clip = copy.deepcopy(mesh)
    vertices = np.asarray(mesh_to_clip.vertices)
    
    # Remove vertices on the right side of the vertical plane (x > plane_center[0])
    vertices_to_remove = vertices[:, 0] > plane_center[0]
    
    mesh_clipped = copy.deepcopy(mesh_to_clip)
    mesh_clipped.remove_vertices_by_mask(vertices_to_remove)
    
    visualize_step(mesh_clipped, "CLIPPED MESH", 6)
    
    print(f"Number of remaining vertices: {len(mesh_clipped.vertices)}")
    print(f"Number of remaining triangles: {len(mesh_clipped.triangles)}")
    print(f"Has vertex colors: {mesh_clipped.has_vertex_colors()}")
    print(f"Has vertex normals: {mesh_clipped.has_vertex_normals()}")
    
    # Step 7: Working with Color and Extremes
    # Создаем копию для окрашивания
    colored_mesh = copy.deepcopy(mesh)
    
    # Удаляем старые цвета если есть
    if colored_mesh.has_vertex_colors():
        colored_mesh.vertex_colors = o3d.utility.Vector3dVector()
    
    # Применяем градиент по Y-axis (высота)
    vertices = np.asarray(colored_mesh.vertices)
    y_coords = vertices[:, 1]  # Y-координата для градиента по высоте
    y_min, y_max = np.min(y_coords), np.max(y_coords)
    
    # Создаем цвета от синего (низ) к красному (верх)
    colors = np.zeros_like(vertices)
    for i, y in enumerate(y_coords):
        t = (y - y_min) / (y_max - y_min) if y_max != y_min else 0.5
        # Градиент: синий -> фиолетовый -> красный
        colors[i] = [t, 0.2, 1 - t]
    
    colored_mesh.vertex_colors = o3d.utility.Vector3dVector(colors)
    
    # Находим экстремальные точки по Y-axis
    min_idx = np.argmin(y_coords)
    max_idx = np.argmax(y_coords)
    min_point = vertices[min_idx]
    max_point = vertices[max_idx]
    
    # Создаем сферы для выделения экстремальных точек
    sphere_radius = max(bbox_size) * 0.03  # Автоматический размер
    
    min_sphere = o3d.geometry.TriangleMesh.create_sphere(radius=sphere_radius)
    min_sphere.paint_uniform_color([0, 1, 0])  # Зеленая - минимум
    min_sphere.translate(min_point)
    
    max_sphere = o3d.geometry.TriangleMesh.create_sphere(radius=sphere_radius)
    max_sphere.paint_uniform_color([1, 0, 0])  # Красная - максимум
    max_sphere.translate(max_point)
    
    visualize_step([colored_mesh, min_sphere, max_sphere], "COLORED MESH WITH EXTREMES", 7)
    
    print(f"Minimum point (Y-axis): ({min_point[0]:.3f}, {min_point[1]:.3f}, {min_point[2]:.3f})")
    print(f"Maximum point (Y-axis): ({max_point[0]:.3f}, {max_point[1]:.3f}, {max_point[2]:.3f})")
    
    print("\n" + "=" * 70)
    print("🎉 ALL 7 STEPS COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    main()