double lumiXsecWeight(double luminosity, double Xsection, double weightSum, double genWeight)
{
    return (luminosity * Xsection * genWeight / weightSum);
}
