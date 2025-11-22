import os
import pandas as pd
from neo4j import GraphDatabase
from dotenv import load_dotenv
import time

load_dotenv()

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
AUTH = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "password"))

class GraphLoader:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)
        self.verify_connection()

    def verify_connection(self):
        try:
            self.driver.verify_connectivity()
            print("Connected to Neo4j")
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self):
        self.driver.close()

    def create_indexes(self):
        print("Creating indexes...")
        queries = [
            "CREATE INDEX node_id_index IF NOT EXISTS FOR (n:Entity) ON (n.id)",
            "CREATE INDEX node_name_index IF NOT EXISTS FOR (n:Entity) ON (n.name)",
            "CREATE INDEX node_type_index IF NOT EXISTS FOR (n:Entity) ON (n.type)"
        ]
        with self.driver.session() as session:
            for q in queries:
                session.run(q)
        print("Indexes created.")

    def load_nodes(self, nodes_file):
        print(f"Loading nodes from {nodes_file}...")
        # Read CSV in chunks to avoid memory issues
        chunk_size = 10000
        total_nodes = 0
        
        # Query to create nodes
        # We use MERGE to avoid duplicates, but CREATE is faster if we are sure.
        # Given it's a fresh load, we can use UNWIND + MERGE/CREATE
        query = """
        UNWIND $batch AS row
        MERGE (n:Entity {id: row.node_id})
        SET n.name = row.node_name,
            n.type = row.node_type,
            n.source = row.node_source,
            n.index = row.node_index
        """
        
        with self.driver.session() as session:
            for chunk in pd.read_csv(nodes_file, chunksize=chunk_size):
                batch = chunk.to_dict('records')
                session.run(query, batch=batch)
                total_nodes += len(batch)
                print(f"Loaded {total_nodes} nodes...", end='\r')
        print(f"\nFinished loading {total_nodes} nodes.")

    def load_edges(self, edges_file):
        print(f"Loading edges from {edges_file}...")
        chunk_size = 10000
        total_edges = 0
        
        # Query to create relationships
        # We match nodes by ID and create the relationship
        query = """
        UNWIND $batch AS row
        MATCH (source:Entity {id: row.x_id})
        MATCH (target:Entity {id: row.y_id})
        MERGE (source)-[r:RELATED_TO {type: row.relation, display: row.display_relation}]->(target)
        """
        
        with self.driver.session() as session:
            for chunk in pd.read_csv(edges_file, chunksize=chunk_size):
                # Ensure IDs are strings/integers consistent with nodes
                batch = chunk.to_dict('records')
                session.run(query, batch=batch)
                total_edges += len(batch)
                print(f"Loaded {total_edges} edges...", end='\r')
        print(f"\nFinished loading {total_edges} edges.")

    def load_disease_features(self, features_file):
        print(f"Loading disease features from {features_file}...")
        chunk_size = 5000
        count = 0
        
        # Match by node_index (assuming it aligns with nodes.csv) or we might need to match by name/id.
        # PrimeKG usually aligns node_index. Let's try matching by node_index if we loaded it, 
        # or we can match by node_id if available. 
        # Looking at the CSV, it has node_index.
        # We need to ensure we stored node_index in load_nodes. 
        # Wait, load_nodes stored `id: row.node_id`. It didn't store node_index.
        # Let's check nodes.csv header again: node_index,node_id,node_type,node_name,node_source
        # We should probably store node_index in load_nodes to make this easy, or match by something else.
        # disease_features.csv has: node_index, mondo_id, ...
        
        # Let's update the query to match by node_index if possible, but we didn't save it.
        # We can match by 'id' if disease_features has the same ID.
        # disease_features: node_index, mondo_id... 
        # nodes.csv: node_index, node_id...
        # It's likely node_id in nodes.csv == mondo_id in disease_features for diseases.
        # But to be safe, let's rely on node_index if we can. 
        # I will update load_nodes to save node_index as a property 'index' temporarily or permanently.
        
        query = """
        UNWIND $batch AS row
        MATCH (n:Entity) WHERE n.index = row.node_index
        SET n.definition = row.mondo_definition,
            n.mayo_symptoms = row.mayo_symptoms,
            n.mayo_causes = row.mayo_causes,
            n.orphanet_description = row.orphanet_clinical_description
        """
        
        with self.driver.session() as session:
            for chunk in pd.read_csv(features_file, chunksize=chunk_size):
                # Fill NaNs to avoid Neo4j errors
                chunk = chunk.fillna("")
                batch = chunk.to_dict('records')
                session.run(query, batch=batch)
                count += len(batch)
                print(f"Loaded features for {count} diseases...", end='\r')
        print(f"\nFinished loading disease features.")

    def load_drug_features(self, features_file):
        print(f"Loading drug features from {features_file}...")
        chunk_size = 5000
        count = 0
        
        query = """
        UNWIND $batch AS row
        MATCH (n:Entity) WHERE n.index = row.node_index
        SET n.mechanism = row.mechanism_of_action,
            n.indication = row.indication,
            n.pharmacodynamics = row.pharmacodynamics
        """
        
        with self.driver.session() as session:
            for chunk in pd.read_csv(features_file, chunksize=chunk_size):
                chunk = chunk.fillna("")
                batch = chunk.to_dict('records')
                session.run(query, batch=batch)
                count += len(batch)
                print(f"Loaded features for {count} drugs...", end='\r')
        print(f"\nFinished loading drug features.")

def main():
    loader = GraphLoader(URI, AUTH)
    try:
        loader.create_indexes()
        
        # Paths to files
        base_path = "Docs/dataverse-files"
        nodes_path = os.path.join(base_path, "nodes.csv")
        edges_path = os.path.join(base_path, "kg.csv")
        disease_feat_path = os.path.join(base_path, "disease_features.csv")
        drug_feat_path = os.path.join(base_path, "drug_features.csv")
        
        if os.path.exists(nodes_path):
            loader.load_nodes(nodes_path)
            # Create index on 'index' property for fast feature loading
            with loader.driver.session() as session:
                session.run("CREATE INDEX node_index_idx IF NOT EXISTS FOR (n:Entity) ON (n.index)")
        else:
            print(f"File not found: {nodes_path}")
            
        if os.path.exists(disease_feat_path):
            loader.load_disease_features(disease_feat_path)
            
        if os.path.exists(drug_feat_path):
            loader.load_drug_features(drug_feat_path)

        if os.path.exists(edges_path):
            loader.load_edges(edges_path)
        else:
            print(f"File not found: {edges_path}")
            
    finally:
        loader.close()

if __name__ == "__main__":
    main()
