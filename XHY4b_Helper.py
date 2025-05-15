import numpy as np
import array
from hist import Hist
import ROOT

def rebin_TH1(h, bins, name = "default"):
    nbins_ori = h.GetNbinsX()
    bins_ori = [h.GetXaxis().GetBinLowEdge(i) for i in range(1, nbins_ori +1) ]
    bins_ori.append(h.GetXaxis().GetBinUpEdge(nbins_ori))
    bins_map = np.zeros(len(bins), dtype = int) - 1
    for i in range(len(bins)):
        bin_edge = bins[i]
        for j in range(len(bins_ori)):
            bin_edge_ori = bins_ori[j]
            if abs(bin_edge_ori - bin_edge) < (1e-6 * (bins[1] - bins[0] )):
                bins_map[i] = j
                break
        if bins_map[i] == -1:
           print(f"Bins of the input TH1:", bins_ori)
           raise ValueError(f"Bin edge {bin_edge} not found in the input TH1") 
    if name == "default":
        name = h.GetName() + "_merged"
    title = h.GetTitle() 
    h_merged = ROOT.TH1D(name, title, len(bins) - 1, bins)
    for i in range(len(bins) - 1):
        value = 0
        sigma = 0
        low_index = bins_map[i]
        up_index = bins_map[i + 1]
        for j in range(low_index, up_index):
            value += h.GetBinContent(j + 1)
            sigma += np.sqrt(sigma**2 + h.GetBinError(j + 1)**2)
        h_merged.SetBinContent(i + 1, value)
        h_merged.SetBinError(i + 1, sigma)
    return h_merged
         
  
    
    
    
def rebin_TH2(h, xbins, ybins, name = "default"):
    nbins_ori_x = h.GetNbinsX()
    nbins_ori_y = h.GetNbinsY()
    
    bins_ori_x = [h.GetXaxis().GetBinLowEdge(i) for i in range(1, nbins_ori_x +1) ]
    bins_ori_y = [h.GetYaxis().GetBinLowEdge(i) for i in range(1, nbins_ori_y +1) ]
    bins_ori_x.append(h.GetXaxis().GetBinUpEdge(nbins_ori_x))
    bins_ori_y.append(h.GetYaxis().GetBinUpEdge(nbins_ori_y))
    bins_map_x = np.zeros(len(xbins), dtype = int) - 1
    bins_map_y = np.zeros(len(ybins), dtype = int) - 1
    for i in range(len(xbins)):
        bin_edge_x = xbins[i]
        for j in range(len(bins_ori_x)):
            bin_edge_ori_x = bins_ori_x[j]
            
            if abs(bin_edge_ori_x - bin_edge_x) < (1e-6 * (xbins[1] - xbins[0]) ):
                bins_map_x[i] = j
                break
        if bins_map_x[i] == -1:
           print(f"XBins of the input TH2:", bins_ori_x)
           raise ValueError(f"XBin edge {bin_edge_x} not found in the input TH2") 
    for i in range(len(ybins)):
        bin_edge_y = ybins[i]
        for j in range(len(bins_ori_y)):
            bin_edge_ori_y = bins_ori_y[j]
            if abs(bin_edge_ori_y - bin_edge_y) < (1e-6 * (ybins[1] - ybins[0]) ):
                bins_map_y[i] = j
                break
        if bins_map_y[i] == -1:
           print(f"YBins of the input TH2:", bins_ori_x)
           raise ValueError(f"YBin edge {bin_edge_y} not found in the input TH2") 
    title = h.GetTitle() 
    if name == "default":
        name = h.GetName() + "_merged"
    h_merged = ROOT.TH2D(name, title, len(xbins) - 1, xbins, len(ybins) - 1, ybins)
    for i in range(len(xbins) - 1):
        for j in range(len(ybins) - 1):
            value = 0
            sigma = 0
            low_index_x = bins_map_x[i]
            up_index_x = bins_map_x[i + 1]
            low_index_y = bins_map_y[j]
            up_index_y = bins_map_y[j + 1]
            for m in range(low_index_x, up_index_x):
                for n in range(low_index_y, up_index_y):
                    value += h.GetBinContent(m + 1, n + 1)
                    sigma += np.sqrt(sigma**2 + h.GetBinError(m + 1, n + 1)**2)
            h_merged.SetBinContent(i + 1, j + 1, value)
            h_merged.SetBinError(i + 1, j + 1, sigma)
    return h_merged
         
  
    
    
    
