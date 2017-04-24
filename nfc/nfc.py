from ctypes import *

debug = True

libnfc = CDLL("libnfc.so")

class nfc_baud_rate:
    NBR_UNDEFINED = 0
    NBR_106 = 1
    NBR_212 = 2
    NBR_424 = 3
    NBR_847 = 4

class nfc_modulation_type:
    NMT_ISO14443A = 1,
    NMT_JEWEL = 2
    NMT_ISO14443B = 3
    NMT_ISO14443BI = 4 # pre-ISO14443B aka ISO/IEC 14443 B' or Type B'
    NMT_ISO14443B2SR = 5 # ISO14443-2B ST SRx
    NMT_ISO14443B2CT = 6 # ISO14443-2B ASK CTx
    NMT_FELICA = 7
    NMT_DEP = 8

DEVICE_NAME_LENGTH = 256
NFC_BUFSIZE_CONNSTRING = 1024

class nfc_context(Structure):
    pass

nfc_context_p = POINTER(nfc_context)

#class nfc_device(Structure):
    #pass
    #_fields_ = [("context", POINTER(nfc_context)),
    #            ("driver", c_void_p),
    #            ("driver_data", c_void_p),
    #            ("chip_data", c_void_p),
    #            ("name", c_char * DEVICE_NAME_LENGTH),
    #            ("connstring", c_char * NFC_BUFSIZE_CONNSTRING),
    #            ("bCrc", c_byte),
    #            ("bPar", c_byte),
    #            ("bEasyFraming", c_byte),
    #            ("bInfiniteSelect", c_byte),
    #            ("bAutoIso14443_4", c_byte),
    #            ("btSupportByte", c_ubyte),
    #            ("last_error", c_byte)]

#nfc_device_p = POINTER(nfc_device)

class nfc_modulation(Structure):
    _fields_ = [("nmt", c_int),
                ("nbr", c_int)]

class nfc_iso14443a_info(Structure):
    _fields_ = [("abtAtqa", c_ubyte * 2),
                ("btSak", c_ubyte),
                ("szUidLen", c_int),
                ("abtUid", c_ubyte * 10),
                ("szAtsLen", c_int),
                ("abtAts", c_ubyte * 254)] # Maximal theoretical ATS is FSD-2, FSD=256 for FSDI=8 in RATS

class nfc_target_info(Union):
    _fields_ = [("nai", nfc_iso14443a_info)]
                #("nbi", nfc_iso14443b_info),
                #("nii", nfc_iso14443bi_info),
                #("nsi", nfc_iso14443b2sr_info),
                #("nci", nfc_iso14443b2ct_info),
                #("nji", nfc_jewel_info),
                #("ndi", nfc_dep_info)]

class nfc_target(Structure):
    _fields_ = [("nti", nfc_target_info),
                ("nm", nfc_modulation)]

# Return type declarations
libnfc.nfc_device_get_name.restype = c_char_p
#libnfc.nfc_open.restype = nfc_device_p

# Functions
def nfc_open():
    context = nfc_context_p()
    libnfc.nfc_init(pointer(context))

    if (None == context):
        print "Error: Unable to init libnfc"
        return None

    pnd = None
    pnd = libnfc.nfc_open(context, None)

    if (None == pnd):
        print "Error: Unable to open NFC device."
        return None

    if (libnfc.nfc_initiator_init(pnd) < 0):
        print "Error: Failed to init NFC device."
        return None

    if debug:
        deviceName = libnfc.nfc_device_get_name( pnd )
        print "NFC reader: {0} opened\n".format( deviceName )

    return [context, pnd]

def nfc_close(context, pnd):
    libnfc.nfc_close(pnd)
    libnfc.nfc_exit(context)

    if debug:
        print "NFC reader closed"


def nfc_poll( pnd, uiPollNr, uiPeriod ):
    if debug:
        print "Polling {0} times for {1}ms".format( uiPollNr, (uiPeriod * 150) )
