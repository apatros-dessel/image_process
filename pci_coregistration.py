from geodata import *

def pci_auto_coregistration(i_image, reference_image, geo_correct_image, in_match_chan = [1], ref_match_chan = [1], bxpxsz="2.1", polyorder=[1], reject = [5, 1, 1], tresh=[0.88]):
    try:
        from pci.link import link
        from pci.autogcp2 import autogcp2
        from pci.gcprefn import gcprefn
        from pci.polymodel import polymodel
        from pci.ortho2 import ortho2
        ingest_link_file = i_image.split('.')[0]+'.pix'

        if os.path.exists(ingest_link_file):
            os.remove(ingest_link_file)

        link( i_image, ingest_link_file, [] )
        increase_radius = 0
        num_gcps = [0]

        while ((int(num_gcps[0]) > 6) == True) !=  ((increase_radius < 100) == True):
            search_radius = [15+increase_radius]
            smplsrc="GRID:256"
            algo="FFTP"
            gcp_seg = autogcp2( ingest_link_file, in_match_chan, u"", [], [], reference_image, ref_match_chan,
                                u"", [], [], u"", u"", [], smplsrc, algo, search_radius, u"", tresh, u"", num_gcps )
            increase_radius+=15
            tresh=[tresh[0]-0.01]

            if increase_radius>60:
                break

        reject = reject
        refined_gcp_seg = []
        out_stats = []
        gcprefn( ingest_link_file, [gcp_seg[-1]], [], [], "POLY", [], reject, "NO", refined_gcp_seg, out_stats )
        polymodel( ingest_link_file, [refined_gcp_seg[0]], polyorder, [] )
        ortho2(ingest_link_file, [], [], [], "", geo_correct_image, "TIF", "", [], "", "", "",
                "", [], "", "", bxpxsz, "", "", [], [], "", "", [], "", [], "")

        if os.path.exists(ingest_link_file):
            os.remove(ingest_link_file)

        return out_stats

    except:
        return []

# Make pansharpened image
def image_psh(ms, pan, psh, bands, bands_ref, enhanced):
    from pci.pansharp import *
    from pci.fexport import *
    fili = ms
    dbic = bands
    dbic_ref = bands_ref
    fili_pan = pan
    dbic_pan = [1]
    filo = psh.replace('.tif','.pix')
    dboc = dbic
    enhance = enhanced     # apply the color enhancement operation
    nodatval = [0.0]       # zero-valued pixels in any input image are excluded from processing
    poption = "OFF"        # resampling used to build pyramid overview images
    pansharp(fili, dbic, dbic_ref, fili_pan, dbic_pan, filo, dboc, enhance, nodatval, poption)
    fili = filo
    filo = psh
    dbiw = []
    dbic = dbic
    dbib = []
    dbvs = []
    dblut = []
    dbpct = []
    ftype =	"TIF"
    foptions = "TILED256"
    fexport( fili, filo, dbiw, dbic, dbib, dbvs, dblut, dbpct, ftype, foptions )
    if os.path.exists(filo):
        for file in (fili, filo+'.pox'):
            if os.path.exists(file):
                os.remove(file)

i_image = r'C:\Users\Home\Desktop\test_blue_orig.tif'
reference_image = r'F:/102_2020_108_RP/2020-02-02/2074508_22.01.20_Krym/RP1_36120_04_GEOTON_20191209_080522_080539.SCN1.MS_f13121466d65e41f5c181c84cb2e23d2c0553d9a/RP1_36120_04_GEOTON_20191209_080522_080539.SCN1.MS.L2.tif'
geo_correct_image = r'C:\Users\Home\Desktop\test_blue_pci.tif'
in_match_chan = [1]
ref_match_chan = [1]

pci_auto_coregistration(i_image, reference_image, geo_correct_image, in_match_chan = in_match_chan, ref_match_chan = ref_match_chan, bxpxsz="2.1", polyorder=[1], reject = [5, 1, 1], tresh=[0.88])
