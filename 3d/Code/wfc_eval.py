import bpy
import math
from collections import defaultdict
import numpy as np
import bmesh

#Helpers
th = bpy.data.texts["generate_tiles_helpers.py"].as_module()
df_module = bpy.data.texts["dataframe.py"].as_module()
rules = bpy.data.texts["rules.py"].as_module()

# Berechnung der Entropie
# Shannon-Entropie Eine hohe Entropie bedeutet hohe Unsicherheit oder hohe Unordnung. 
# Dies tritt auf, wenn die Wahrscheinlichkeitsverteilung flach ist, 
# d.h., alle Ereignisse sind fast gleich wahrscheinlich.
def calculate_entropy(weights):
    entropy = 0
    for weight in weights:
        if weight > 0 and weight < 1:
            entropy -= weight * math.log2(weight) + (1 - weight) * math.log2(1 - weight)
    return entropy

# Gewichte der Vertex-Gruppen für ein Mesh-Objekt holen
def get_vertex_group_weights(mesh_object):
    vertex_group_weights = defaultdict(list)
    for vertex in mesh_object.data.vertices:
        for group in vertex.groups:
            vg_name = mesh_object.vertex_groups[group.group].name
            vertex_group_weights[vg_name].append(group.weight)
    return vertex_group_weights

# Höchste Gewichte jeder Vertex-Gruppe für jeden Vertex holen
def get_highest_weights_per_vertex(mesh_object):
    highest_weights = defaultdict(list)
    vertex_count_per_type = defaultdict(int)
    for vertex in mesh_object.data.vertices:
        vg_weights = {}
        for group in vertex.groups:
            vg_name = mesh_object.vertex_groups[group.group].name
            vg_weights[vg_name] = group.weight
        
        if vg_weights:
            max_vg = max(vg_weights, key=vg_weights.get)
            highest_weight = vg_weights[max_vg]
            highest_weights[max_vg].append(highest_weight)
            vertex_count_per_type[max_vg] += 1
    
    return highest_weights, vertex_count_per_type

# Initiale Entropie der Vertex-Gruppen berechnen
def calculate_initial_entropy(mesh_object):
    initial_weights = get_vertex_group_weights(mesh_object)
    initial_entropy = {vg: calculate_entropy(weights) for vg, weights in initial_weights.items()}
    return initial_entropy

#Spezielle Kriterien zur Stadtbewertung
def check_criteria(mesh_object,vert,type_name):
    neighbors = th.get_neigbour_verts(vert)
    neighbor_types = [th.get_highest_weight_vertex_group_name(mesh_object, neighbor) for neighbor in neighbors]
    
    if type_name == "river":
        return neighbor_types.count("river") >= 2
    elif type_name == "highway":
        return neighbor_types.count("highway") >= 2
    elif type_name == "road":
        return (neighbor_types.count("road") >= 2) or (neighbor_types.count("road") >= 1 and neighbor_types.count("highway") >= 1)
    elif type_name == "house":
        return (neighbor_types.count("house") >= 1 and ("road" in neighbor_types or "highway" in neighbor_types))
    elif type_name == "industrial":
        return (neighbor_types.count("industrial") >= 2) or (("road" in neighbor_types or "highway" in neighbor_types) and neighbor_types.count("industrial") >= 1)
    elif type_name == "park":
        return (neighbor_types.count("park") >= 2 or (neighbor_types.count("house") >= 1 and neighbor_types.count("park") >= 1))
    return False


# Qualität bewerten
def evaluate_quality(mesh_object, initial_entropy):
    bm = bmesh.new()
    bm.from_mesh(mesh_object.data)
    
    current_weights = get_vertex_group_weights(mesh_object)
    current_highest_weights, vertex_count_per_type = get_highest_weights_per_vertex(mesh_object)
    
    current_entropy = {vg: calculate_entropy(weights) for vg, weights in current_weights.items()}
    current_averages = {vg: np.mean(weights) for vg, weights in current_highest_weights.items()}
    
    total_vertices = len(mesh_object.data.vertices)
    criteria_fulfilled_counts = defaultdict(int)
    
    print()
    print("-------Evaluation Begin-------------")
    for vert in bm.verts:
        vert_type = th.get_highest_weight_vertex_group_name(mesh_object, vert)
        if check_criteria(mesh_object, vert, vert_type):
            criteria_fulfilled_counts[vert_type] += 1
    
    total_criteria_fulfilled = sum(criteria_fulfilled_counts.values())
    overall_criteria_fulfilled_percentage = (total_criteria_fulfilled / total_vertices) * 100 if total_vertices > 0 else 'N/A'
    
    for vg in current_entropy:
        print(f"Vertex Group: {vg}")
        initial_ent = initial_entropy.get(vg, 'N/A')
        current_ent = current_entropy[vg]
        print(f"Initial Entropy: {initial_ent}")
        print(f"Current Entropy: {current_ent}")
        
        if vg in initial_entropy:
            if current_ent < initial_ent:
                #print("Entropy has decreased.")
                reduction_percentage = ((initial_ent - current_ent) / initial_ent) * 100
                print(f"Entropy Reduction Percentage: {reduction_percentage:.2f}%")
            else:
                #print("Entropy has not decreased.")
                print("Entropy Reduction Percentage: 0.00%")
        else:
            print("No initial entropy available.")
        
        print(f"Average Weight when assigned: {current_averages.get(vg, 'N/A')}")
        
        # Drucke die neue Metrik
        vertex_count = vertex_count_per_type.get(vg, 0)
        if total_vertices > 0:
            percentage = (vertex_count / total_vertices) * 100
        else:
            percentage = 'N/A'
        print(f"Count of '{vg}' Vertices: {vertex_count}")
        print(f"Percentage of '{vg}' Vertices: {percentage if percentage == 'N/A' else f'{percentage:.2f}%'}")
        
        criteria_fulfilled_count = criteria_fulfilled_counts.get(vg, 0)
        if vertex_count > 0:
            criteria_fulfilled_percentage = (criteria_fulfilled_count / vertex_count) * 100
        else:
            criteria_fulfilled_percentage = 'N/A'
        print(f"Vertices fulfilling '{vg}' criteria: {criteria_fulfilled_count}")
        print(f"Percentage of '{vg}' criteria fulfillment: {criteria_fulfilled_percentage if criteria_fulfilled_percentage == 'N/A' else f'{criteria_fulfilled_percentage:.2f}%'}")
        print()

    print("Overall Criteria Fulfilled Percentage: ", overall_criteria_fulfilled_percentage if overall_criteria_fulfilled_percentage == 'N/A' else f'{overall_criteria_fulfilled_percentage:.2f}%')
    
    bm.free
    
def evaluate_quality_dataframe(mesh_object, initial_entropy, params):
    bm = bmesh.new()
    bm.from_mesh(mesh_object.data)
    
    current_weights = get_vertex_group_weights(mesh_object)
    current_highest_weights, vertex_count_per_type = get_highest_weights_per_vertex(mesh_object)
    
    current_entropy = {vg: calculate_entropy(weights) for vg, weights in current_weights.items()}
    current_averages = {vg: np.mean(weights) for vg, weights in current_highest_weights.items()}
    
    total_vertices = len(mesh_object.data.vertices)
    criteria_fulfilled_counts = defaultdict(int)
    
    # Initialisiere den DataFrame
    df = df_module.create_dataframe()
    
    for vert in bm.verts:
        vert_type = th.get_highest_weight_vertex_group_name(mesh_object, vert)
        if check_criteria(mesh_object, vert, vert_type):
            criteria_fulfilled_counts[vert_type] += 1
    
    total_criteria_fulfilled = sum(criteria_fulfilled_counts.values())
    overall_criteria_fulfilled_percentage = (total_criteria_fulfilled / total_vertices) * 100 if total_vertices > 0 else 'N/A'
    
    for vg in current_entropy:
        initial_ent = initial_entropy.get(vg, 'N/A')
        current_ent = current_entropy[vg]
        reduction_percentage = 0
        if vg in initial_entropy and initial_ent != 'N/A':
            if current_ent < initial_ent:
                reduction_percentage = ((initial_ent - current_ent) / initial_ent) * 100
        
        vertex_count = vertex_count_per_type.get(vg, 0)
        percentage = (vertex_count / total_vertices) * 100 if total_vertices > 0 else 'N/A'
        
        criteria_fulfilled_count = criteria_fulfilled_counts.get(vg, 0)
        criteria_fulfilled_percentage = (criteria_fulfilled_count / vertex_count) * 100 if vertex_count > 0 else 'N/A'
        
        data = {
            'Size': params['size'],
            'Highways': params['highways'],
            'Rivers': params['rivers'],
            'River Chance': rules.riv_chance,
            'Road Chance': rules.road_chance,
            'House Chance': rules.house_chance,
            'Industrial Chance': rules.industrial_chance,
            'Park Chance': rules.park_chance,
            'Randomness': rules.randomness,
            'Vertex Group': vg,
            'Initial Entropy': initial_ent,
            'Current Entropy': current_ent,
            'Entropy Reduction Percentage': reduction_percentage if reduction_percentage != 0 else 'N/A',
            'Average Weight': current_averages.get(vg, 'N/A'),
            'Vertex Count': vertex_count,
            'Vertex Percentage': percentage if percentage != 'N/A' else 'N/A',
            'Criteria Fulfilled Count': criteria_fulfilled_count,
            'Criteria Fulfilled Percentage': criteria_fulfilled_percentage if criteria_fulfilled_percentage != 'N/A' else 'N/A'
        }
        
        # Füge die Daten zum DataFrame hinzu
        df = df_module.add_data_to_dataframe(df, data)
    
    print("Overall Criteria Fulfilled Percentage: ", overall_criteria_fulfilled_percentage if overall_criteria_fulfilled_percentage == 'N/A' else f'{overall_criteria_fulfilled_percentage:.2f}%')
    
    bm.free
    
    print(df)
    # Speicher den DataFrame in eine CSV-Datei
    filename = "city_generation_evaluation.csv"
    df_module.save_dataframe_to_csv(df, filename)
