import matplotlib.pyplot as plt
import ROOT
MX =3000
MY = 1000
scatter_file = "root://cmseos.fnal.gov//store/user/xinlongl/XHY4bRun3_selection_2p1/nom_tagged_selected_2p1_SKIM_skimmed_2022EE__SignalMC_XHY4b__MX-3000_MY-1600_n-10000_i-0.root"
scatter_file = f"root://cmseos.fnal.gov//store/user/xinlongl/XHY4bRun3_selection_1p1/nom_tagged_selected_SKIM_skimmed_2022EE__SignalMC_XHY4b__MX-{MX}_MY-{MY}_n-10000_i-0.root"


T_score_H = 0.95
L_score_H = 0.8
Aux_score1_H = 0.55
Aux_score2_H = 0.3
T_score_Y = 0.95
L_score_Y = 0.8
Aux_score1_Y = 0.55
Aux_score2_Y = 0.3
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
'''
ax.axhline(y=T_score_H, color='b', linestyle='-', linewidth=2)
ax.axhline(y=L_score_H, color='b', linestyle='-', linewidth=2)
ax.axvline(x=T_score_Y, color='b', linestyle='-', linewidth=2)
ax.axvline(x=L_score_Y, color='b', linestyle='-', linewidth=2)
ax.axvline(x=Aux_score1_Y, color='b', linestyle='-', linewidth=2)
'''
ax.set_xlabel("H PNet Score", loc = "right")
ax.set_ylabel("Y PNet Score", loc = "top")

ax.set_ylim(Aux_score1_Y, 1)
ax.set_xlim(Aux_score2_H, 1)
'''
Regions = {"SR1":[[T_score_Y, 1], [T_score_H, 1]], 
    "SR2":[[L_score_Y, 1], [L_score_H, 1]], 
    "SB1":[[T_score_Y, 1], [Aux_score1_H, L_score_H]], 
    "SB2": [[L_score_Y, 1], [Aux_score1_H, L_score_H]], 
    "VS1": [[Aux_score1_Y, L_score_Y], [T_score_H, 1]], 
    "VS2" : [[Aux_score1_Y, L_score_Y], [L_score_H, 1]], 
    "VB1": [[Aux_score1_Y, L_score_Y], [Aux_score1_H, L_score_H]], 
    "VS3" : [[Aux_score2_Y, Aux_score1_Y], [T_score_H, 1] ], 
    "VS4" : [[Aux_score2_Y, Aux_score1_Y], [L_score_H, 1]], 
    "VB2" : [[Aux_score2_Y, Aux_score1_Y], [Aux_score1_H, L_score_H]]
}
'''
Regions = {"SR1":[[T_score_H, 1], [T_score_Y, 1]], 
    "SR2":[[L_score_H, 1], [L_score_Y, 1]], 
    "SB1":[[T_score_H, 1], [Aux_score1_Y, L_score_Y]], 
    "SB2": [[L_score_H, 1], [Aux_score1_Y, L_score_Y]], 
    "VS1": [[Aux_score1_H, L_score_H], [T_score_Y, 1]], 
    "VS2" : [[Aux_score1_H, L_score_H], [L_score_Y, 1]], 
    "VB1": [[Aux_score1_H, L_score_H], [Aux_score1_Y, L_score_Y]], 
    "VS3" : [[Aux_score2_H, Aux_score1_H], [T_score_Y, 1] ], 
    "VS4" : [[Aux_score2_H, Aux_score1_H], [L_score_Y, 1]], 
    "VB2" : [[Aux_score2_H, Aux_score1_H], [Aux_score1_Y, L_score_Y]]
}
rdf = ROOT.RDataFrame("Events", scatter_file)
#rdf = rdf.Define("PNet_Y", "std::min(PNet_Y0, PNet_Y1)")
rdf_np = rdf.AsNumpy(["PNet_Y", "PNet_H"])
print(rdf_np)
#ax.scatter(rdf_np["PNet_H"], rdf_np["PNet_Y"], s = 1, color='black', marker='o')
Ns = {"SR1": 0, "SR2": 0, "SB1": 0, "SB2": 0, "VS1": 0, "VS2": 0, "VB1": 0, "VS3": 0, "VS4": 0, "VB2": 0}
for i in range(len(rdf_np["PNet_Y"])):
    pnet_y = rdf_np["PNet_H"][i]
    pnet_h = rdf_np["PNet_Y"][i]
    for region in Regions:
        if pnet_y > Regions[region][0][0] and pnet_y < Regions[region][0][1] and pnet_h > Regions[region][1][0] and pnet_h < Regions[region][1][1]:
            Ns[region] = Ns[region] + 1
for region in Regions:
    center_x = (Regions[region][0][0] + Regions[region][0][1]) / 2
    center_y = (Regions[region][1][0] + Regions[region][1][1]) / 2
    ax.hlines(y=Regions[region][1][0], xmin = Regions[region][0][0], xmax = Regions[region][0][1], color='b', linestyle='-', linewidth=2)
    ax.hlines(y=Regions[region][1][1], xmin = Regions[region][0][0], xmax = Regions[region][0][1], color='b', linestyle='-', linewidth=2)
    ax.vlines(x=Regions[region][0][0], ymin = Regions[region][1][0], ymax = Regions[region][1][1], color='b', linestyle='-', linewidth=2)
    ax.vlines(x=Regions[region][0][1], ymin = Regions[region][1][0], ymax = Regions[region][1][1], color='b', linestyle='-', linewidth=2)
    ax.text(
        #center_x, center_y, region + f" {Ns[region]}",
        center_x, center_y, region,
        ha='center', va='center',
        fontsize=12, color='red'
    )
print(Ns)
#ax.set_title(f"1p1 MX-{MX} MY-{MY} scattering distribution")
ax.set_title(f"1p1 Region Defination")
#fig.savefig(f"Regions_MX{MX}_MY{MY}_1p1.png")
fig.savefig(f"Regions_1p1.png")
