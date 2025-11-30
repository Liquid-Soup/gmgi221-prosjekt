import os
import glob
import geopandas as gpd
import osmnx as ox
import contextily as ctx
import matplotlib.pyplot as plt
import xyzservices.providers as xyz

def bygg_graf(area_dict, network_type = "drive"):
    """
    Tar en dictionary med adresser og returnerer 
    gatenettverk, nodes og edges for et gitt område definert ved et stedsnavn.
    """
    # Tomme dicts for informasjonsskrving
    graphs = {}
    nodes = {}
    edges = {}

    for navn, sted in area_dict.items():
        print(f"Henter data for {sted} ...")
        # Henter ut selve grafen
        G = ox.graph_from_place(sted, network_type=network_type)
        # Fra graf, henter nodes og edges
        g_nodes, g_edges = ox.graph_to_gdfs(G)
        #Sriver til dictionaries
        graphs[navn] = G
        nodes[navn] = g_nodes
        edges[navn] = g_edges
        print(f"Innehneting av data for {sted} velykket!")

    #returnerer dictionaries med grafer, nodes og edges
    return graphs, nodes, edges

def sted_til_poly(area_dict, crs="EPSG:25833"):
    """
    Tar en dict med grafer, evt crs og returnerer polygonet
    """
    polygons = {}

    for navn, sted in area_dict.items():

        # konverterer geodataframe
        gdf = ox.geocode_to_gdf(sted).to_crs(crs)
        # geometrien befinner seg i første kolonne
        poly = gdf.iloc[0]
        # Returnerer polygonet
        polygons[navn] = poly

    return polygons



def beregn_gatetetthet(graf_dict, poly_dict):
    """
    Tar to dictionaries med grafer og polygoner og returner den totale veilengden for områdene
    """
    
    resultater = {}

    # løkke som iterer over graf_dict og returnerer veilengden
    for navn in graf_dict:
        
        # utnytter navn som felles nøkkel
        graf = graf_dict[navn]
        poly = poly_dict[navn]

        # må ha "undirected" graf for street_length_total
        ug = ox.convert.to_undirected(graf)
        # gir lengden av veinettverket i meter
        veilengde_m = ox.stats.street_length_total(ug)

        # Henter ut areal til polygonet
        areal_km2 = poly["geometry"].area

        # Beregner gatetetthet i km/per km^2
        gatetetthet = (veilengde_m / 1000) / (areal_km2 / 1_000_000)
        
        # skriver alt til resultater
        resultater[navn] = {
        "veilengde": veilengde_m,
        "polygon": poly,
        "areal": areal_km2,
        "gatetetthet": gatetetthet
    }

    return resultater

def plot_gatetetthet(gatetetthet_dict, crs="EPSG:25833"):

    """
    Konverterer poly dict til geodataframe og plotter
    """

    to_plot = []

    # iterer over gatetetthet dictionarien og henter ut navn, geometri og gattetetthet som dictionary
    # og appender til to_plot
    for navn, egenskaper in gatetetthet_dict.items():
        to_plot.append({
            "område": navn,
            "geometry": egenskaper["polygon"]["geometry"],
            "gatetetthet": egenskaper["gatetetthet"]
        })

    # konverterer to_plot til gdf, og setter utm crs for plotting
    gdf = gpd.GeoDataFrame(to_plot, geometry="geometry", crs=crs)

    fig, ax = plt.subplots(figsize=(10, 6))

    gdf.plot(
        ax=ax,
        column="gatetetthet",
        cmap="viridis",  
        edgecolor="black",
        legend=True,
        legend_kwds={
            "label": "Gatetetthet (km vei per km²)"
        }
    )

    ax.set_title("Gatetetthet for områder", fontsize=14)

    ctx.add_basemap(
        ax,
        crs=gdf.crs,
        source=xyz.OpenStreetMap.HOT
    )

    plt.tight_layout()
    plt.show()

def beregn_degree(grafer_dict):
    """
    Tar dict grafer og noder, returnerer en dict med stedsnavn og node degrees
    """
    # tom dictionary jeg skriver til
    degree_dict = {}

    # Iterer over hvert områdes graf 
    # henter ut per område degree dict
    for navn, graf in grafer_dict.items():
        degree_dict[navn] = dict(graf.degree())
    
    return degree_dict

def beregn_betweenness(grafer, edges_dict):
    pass

def bygg_indikator_tabell():
    pass

