""" irdata load """ 

def main():
    model.Base.metadata.bind = sa.create_engine("postgresql://jeff@localhost/irdata")
    model.Base.metadata.drop_all(checkfirst=True)
    model.Base.metadata.create_all(checkfirst=True)
    ## Load data from cow system
    load_cow_states(open("external/www.correlatesofwar.org/COW2 Data/SystemMembership/2008/states2008.1.csv", 'rb'))
    load_cow_majors(open("external/www.correlatesofwar.org/COW2 Data/SystemMembership/2008/majors2008.1.csv", 'rb'))
    load_cow_system()
    load_ksg_states(open("external/privatewww.essex.ac.uk/~ksg/data/iisystem.dat", 'rb'),
                    open("external/privatewww.essex.ac.uk/~ksg/data/microstatessystem.dat", 'rb'))
    load_ksg_system()
    load_ksg2cow()
    load_nmc_codes(open("data/nmc_codes.yaml", 'r'))
    ## If not opened with rU then throws 
    load_nmc(zipfile.ZipFile('external/www.correlatesofwar.org/COW2 Data/Capabilities/NMC_Supplement_v4_0_csv.zip').open('NMC_Supplement_v4_0.csv', 'rU'))
    load_polity_states(open('data/polity4_states.yaml', 'r'))
    load_polity(open('data/p4v2010.csv', 'r'))
    load_cow_war_types(open("data/cow_war_types.yaml", "r"))
    load_enum_from_yaml(open("data/war4_enum.yaml", "r"))
    load_war4(open("data/InterStateWarData_v4.0.csv", 'rU'))
    load_war4_intra(open("data/IntraStateWarData_v4.1.csv", 'rU'))
    load_enum_from_yaml(open("data/war3_enum.yaml", 'r'))
    load_war3(open("external/www.correlatesofwar.org/cow2 data/WarData/InterState/Inter-State Wars (V 3-0).csv", 'r'))
    load_war3_partic(open("external/www.correlatesofwar.org/cow2 data/WarData/InterState/Inter-State War Participants (V 3-0).csv", 'r'))
    load_war3(open("external/www.correlatesofwar.org/cow2 data/WarData/IntraState/Intra-State Wars (V 3-0).csv", 'r'))
    load_war3_partic(open("external/www.correlatesofwar.org/cow2 data/WarData/IntraState/Intra-State War Participants (V 3-0).csv", 'r'))
    load_war3(open("external/www.correlatesofwar.org/cow2 data/WarData/ExtraState/Extra-State Wars (V 3-0).csv", 'r'))
    load_war3_partic(open("external/www.correlatesofwar.org/cow2 data/WarData/ExtraState/Extra-State War Participants (V 3-0).csv", 'r'))
    load_enum_from_yaml(open("data/contiguity_type.yaml", 'r'))
    load_contdir(open("data/DirectContiguity310/contdir.csv", "rU"))

if __name__ == '__main__':
    main()
