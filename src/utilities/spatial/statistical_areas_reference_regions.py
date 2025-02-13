## Reference region functions for selecting different masking regions
# returns a list of statistical region designations for inclusion in masking. 
from src.utilities.spatial.get_sa_codes import get_sa_codes

def state_scope(state, sa_scope):
    # state is a string acronym for state (i.e. NSW, ACT, QLD, WA, SA, NT, TAS, VIC)
    # statistical_area_scope is which scope to use (i.e. 'sa1', 'sa2', 'sa3', 'sa4')
    
    sa_scope_df = get_sa_codes(sa_scope)
    
    if state == 'NSW':
        sa_regions = [x for x in sa_scope_df if str(x)[:1] in ['1']]
    if state == 'QLD':
        sa_regions = [x for x in sa_scope_df if str(x)[:1] in ['3']]
    if state == 'SA':
        sa_regions = [x for x in sa_scope_df if str(x)[:1] in ['4']]
    if state == 'WA':
        sa_regions = [x for x in sa_scope_df if str(x)[:1] in ['5']]
    if state == 'TAS':
        sa_regions = [x for x in sa_scope_df if str(x)[:1] in ['6']]
    if state == 'ACT':
        sa_regions = [x for x in sa_scope_df if str(x)[:1] in ['7']]
    if state == 'NT':
        sa_regions = [x for x in sa_scope_df if str(x)[:1] in ['8']]
    if state == 'VIC':
        sa_regions = [x for x in sa_scope_df if str(x)[:1] in ['2']]

    return sa_regions

def southern_growing_region(sa_scope):
    # this comprises SA, VIC, TAS

    sa_scope_df = get_sa_codes(sa_scope)

    sa_regions = [x for x in sa_scope_df if str(x)[:1] in ['2', '4', '6']]
    
    return sa_regions


