import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.size'] = 16

NUM_BINS = int(2**16)

# 10 unique server colors currently supported 
# while graphing, if you want to plot the 
# results for more servers just add colors
BASE_COLORS = [
    "#9e0142",
    "#f46d43",
    "#fee08b",
    "#e6f598",
    "#abdda4",
    "#66c2a5",
    "#d53e4f",
    "#3288bd",
    "#fdae61",
    "#5e4fa2",
    "#fdae61",
]

def bounded_hash(obj, n_bins=NUM_BINS):
    return hash(obj) % n_bins

def create_virtual_servers_and_hash(N: int, K: int):
    """
    Returns two arrays of len N x K, one with string server names,
    ex: 's0_0', 's3_1', and the other with the bounded hash value
    of the server name. 
    """
    
    servers = ['s' + str(i) for i in range(N)]
    
    # now make k virtual copies of each server 
    virtual_servers = []
    for s in servers:
        for k in range(K):
            virtual_servers.append(s + '_' + str(k))
    
    server_hash = [bounded_hash(s) for s in virtual_servers]
    
    server_hash = np.array(server_hash)
    virtual_servers = np.array(virtual_servers)
    
    return virtual_servers, server_hash

def calculate_url_assignments(N, servers, server_hash):
    """
    Assumes that URLs are uniformly distributed across the hash buckets
    and calculates the number of URLs assigned to each server. A URL is 
    assigned to the server whose hash value most closely precedes the URL's
    own hash value. 
    Example: 
        Server 's1_0' hash value = 14
        Sever 's3_1' hash value = 20
        
        Assuming buckets start at 0, 
            's1_0' has 14 URLs assigned to it
            's3_1' has 6 URLs assigned to it
        
    Returns the URL allocation counts for each virtual server and original server
    """
    sorted_idxs = np.argsort(server_hash)
    
    server_hash = server_hash[sorted_idxs]
    servers = servers[sorted_idxs]
    
    start = 0
    virtual_assignment_count = {}
    for idx in range(len(servers)):
        num_assigned = server_hash[idx] - start
        start = server_hash[idx]
        virtual_assignment_count[servers[idx]] = num_assigned
        
    total_server_assignment_count = {}
    for s in range(N):
        true_server = 's' + str(s)
        server_url_count = sum([val for key, val in virtual_assignment_count.items() if true_server in key])
        total_server_assignment_count[true_server] = server_url_count
        
    return virtual_assignment_count, total_server_assignment_count


def plot_url_allocation(virtual_data, total_data):
    virtual_variance = np.std(np.array([v for v in virtual_data.values()]))
    total_variance = np.std(np.array([v for v in total_data.values()]))
    
    
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    ax = ax.flatten()

    virtual_colors = [BASE_COLORS[int(key.split('_')[0][-1])] for key in virtual_data]
    total_colors = [BASE_COLORS[int(key[-1])] for key in total_data]
    
    ax[0].pie([val for key, val in virtual_data.items()], colors=virtual_colors)
    ax[1].pie([val for key, val in total_data.items()], 
              colors=total_colors, 
              autopct='%1.1f%%',
             pctdistance=1.2)
    ax[0].set_title("Virtual server URL allocations")
    ax[1].set_title("Actual server URL allocations")
    return fig, ax
    

def visualize_server_url_assignments(N=3, K=1):
    """
    Calculates the number of uniformly distributed URLS that would be assigned to a given server 
    based on the URL's hash number. 
    """
    servers, server_hash = create_virtual_servers_and_hash(N, K)
    virtual_assignment_count, total_server_assignment_count = calculate_url_assignments(N, servers, server_hash)
    fig, ax = plot_url_allocation(virtual_assignment_count, total_server_assignment_count)
    fig.suptitle(f"{N} servers, {K} virtual copies", size=20)