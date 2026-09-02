# routes/estamp.py - e-Stamp API Routes
import random
import string
import json
from flask import Blueprint, request, jsonify, session
from models import db, EStamp, EStampConfig, User
from routes.auth import login_required, admin_required

estamp_bp = Blueprint('estamp', __name__)

# ── All 141 Account Reference values ──
ACC_REF_LIST = [
    "NONACC (FI)/ kacrsfl08/ WHITEFIELD2/ KA-GN",
    "NONACC (FI)/ kaksfcl08/ SARJAPUR3/ KA-SV",
    "NONACC (FI)/ kaksfcl08/ ELECTRONIC CITY4/ KA-BA",
    "NONACC (FI)/ kadopkc07/ HEBBAL/ KA-GN",
    "NONACC (FI)/ kakscub08/ BANASHANKARI6/ KA-SV",
    "NONACC (BK)/ kacrsfl08/ BASAVANAGUDI7/ KA-BA",
    "NONACC (FI)/ kakscub08/ JP NAGAR8/ KA-GN",
    "NONACC (FI)/ kacrsfl09/ KENGERI/ KA-SV",
    "NONACC (FI)/ kacrsfl09/ MAGADI ROAD10/ KA-BA",
    "NONACC (FI)/ kakscub08/ PEENYA11/ KA-GN",
    "NONACC (FI)/ kacrsl08/ NELAMANGALA12/ KA-SV",
    "NONACC (BK)/ kacrsl08/ DEVANAHALLI/ KA-BA",
    "NONACC (FI)/ kabacsl08/ ATTIBELE14/ KA-GN",
    "NONACC (FI)/ kakscsa08/ BOMMANAHALLI15/ KA-SV",
    "NONACC (FI)/ kacrsfl09/ HENNUR16/ KA-BA",
    "NONACC (FI)/ kadopkc07/ KADUGODI/ KA-GN",
    "NONACC (FI)/ kacrsfl09/ KUNDALAHALLI18/ KA-SV",
    "NONACC (BK)/ kacrsfl09/ CV RAMAN NAGAR19/ KA-BA",
    "NONACC (FI)/ kabacsl08/ RICHMOND TOWN20/ KA-GN",
    "NONACC (FI)/ kakscsa08/ FRAZER TOWN/ KA-SV",
    "NONACC (FI)/ kacrsfl08/ RT NAGAR22/ KA-BA",
    "NONACC (FI)/ kacrsfl09/ VIDYARANYAPURA23/ KA-GN",
    "NONACC (FI)/ kacrsfl09/ BANASWADI1/ KA-SV",
    "NONACC (BK)/ kacrsfl09/ KASTURINAGAR/ KA-BA",
    "NONACC (FI)/ kagcsl08/ KALASIPALYA3/ KA-GN",
    "NONACC (FI)/ kagcsl09/ MYSORE ROAD4/ KA-SV",
    "NONACC (FI)/ kacrsfl08/ CHICKPET5/ KA-BA",
    "NONACC (FI)/ kakscsa08/ ULSOOR/ KA-GN",
    "NONACC (FI)/ kakscub08/ SADASHIVANAGAR7/ KA-SV",
    "NONACC (BK)/ kagcsl08/ SANJAY NAGAR8/ KA-BA",
    "NONACC (FI)/ kacrsfl09/ JALAHALLI9/ KA-GN",
    "NONACC (FI)/ kagcsl09/ NANDINI LAYOUT/ KA-SV",
    "NONACC (FI)/ kaksfcl08/ CHANDRA LAYOUT11/ KA-BA",
    "NONACC (FI)/ kaksfcl08/ BASAVESHWARANAGAR12/ KA-GN",
    "NONACC (FI)/ kadopkc07/ KENGERI SATELLITE TOWN13/ KA-SV",
    "NONACC (BK)/ kakscsa08/ HOSAKEREHALLI/ KA-BA",
    "NONACC (FI)/ kacrsl08/ ANEKAL15/ KA-GN",
    "NONACC (FI)/ kagcsl08/ BIDADI16/ KA-SV",
    "NONACC (FI)/ kacrsfl08/ RAMANAGARA17/ KA-BA",
    "NONACC (FI)/ kabacsl08/ KANAKAPURA/ KA-GN",
    "NONACC (FI)/ kacrsl08/ MANDYA ROAD19/ KA-SV",
    "NONACC (BK)/ kagcsl09/ MALLESHPALYA20/ KA-BA",
    "NONACC (FI)/ kadopkc07/ VIGNAN NAGAR21/ KA-GN",
    "NONACC (FI)/ kadopkc07/ MUNNEKOLALA/ KA-SV",
    "NONACC (FI)/ kacrsfl08/ PANATHUR23/ KA-BA",
    "NONACC (FI)/ kadopkc07/ HARALUR1/ KA-GN",
    "NONACC (FI)/ kacrsfl08/ KODIGEHALLI2/ KA-SV",
    "NONACC (BK)/ kagcsl09/ VIDYAPEETA/ KA-BA",
    "NONACC (FI)/ kagcsl09/ KAGGADASAPURA4/ KA-GN",
    "NONACC (FI)/ kagcsl09/ NAGASANDRA5/ KA-SV",
    "NONACC (FI)/ kadopkc07/ DASARAHALLI6/ KA-BA",
    "NONACC (FI)/ kaksfcl08/ YASHASWINI NAGAR/ KA-GN",
    "NONACC (FI)/ kacrsl08/ THANISANDRA8/ KA-SV",
    "NONACC (BK)/ kacrsl08/ JAKKUR9/ KA-BA",
    "NONACC (FI)/ kakscub08/ CHIKKABANAVARA10/ KA-GN",
    "NONACC (FI)/ kagcsl08/ KONANAKUNTE/ KA-SV",
    "NONACC (FI)/ kagcsl09/ UTTARAHALLI12/ KA-BA",
    "NONACC (FI)/ kaksfcl08/ SUBRAMANYAPURA13/ KA-GN",
    "NONACC (FI)/ kacrsfl09/ GIRINAGAR14/ KA-SV",
    "NONACC (BK)/ kacrsfl09/ KUMARASWAMY LAYOUT/ KA-BA",
    "NONACC (FI)/ kakscub08/ RR NAGAR16/ KA-GN",
    "NONACC (FI)/ kadopkc07/ BILEKAHALLI17/ KA-SV",
    "NONACC (FI)/ kacrsl08/ HULIMAVU18/ KA-BA",
    "NONACC (FI)/ kacrsl08/ AKSHAYANAGAR/ KA-GN",
    "NONACC (FI)/ kadopkc07/ BEGUR20/ KA-SV",
    "NONACC (BK)/ kabacsl08/ SINGASANDRA21/ KA-BA",
    "NONACC (FI)/ kacrsfl08/ PARAPPANA AGRAHARA22/ KA-GN",
    "NONACC (FI)/ kakscub08/ HONGASANDRA/ KA-SV",
    "NONACC (FI)/ kagcsl08/ KAMAKSHIPALYA1/ KA-BA",
    "NONACC (FI)/ kakscub08/ LAGGERE2/ KA-GN",
    "NONACC (FI)/ kagcsl09/ BYATARAYANAPURA3/ KA-SV",
    "NONACC (BK)/ kacrsfl09/ DODDABALLAPUR/ KA-BA",
    "NONACC (FI)/ kakscsa08/ MADANAYAKANAHALLI5/ KA-GN",
    "NONACC (FI)/ kacrsfl09/ KUMBALGODU6/ KA-SV",
    "NONACC (FI)/ kagcsl08/ VIRGONAGAR7/ KA-BA",
    "NONACC (FI)/ kabacsl08/ MEDAHALLI/ KA-GN",
    "NONACC (FI)/ kacrsfl08/ KR PURAM9/ KA-SV",
    "NONACC (BK)/ kacrsl08/ SEEGEHALLI10/ KA-BA",
    "NONACC (FI)/ kakscub08/ AVALAHALLI11/ KA-GN",
    "NONACC (FI)/ kakscsa08/ KOTHANUR/ KA-SV",
    "NONACC (FI)/ kacrsfl09/ GOTTIGERE13/ KA-BA",
    "NONACC (FI)/ kacrsl08/ CHIKKALLASANDRA14/ KA-GN",
    "NONACC (FI)/ kakscsa08/ WHITEFIELD15/ KA-SV",
    "NONACC (BK)/ kacrsfl08/ SARJAPUR/ KA-BA",
    "NONACC (FI)/ kabacsl08/ ELECTRONIC CITY17/ KA-GN",
    "NONACC (FI)/ kakscsa08/ HEBBAL18/ KA-SV",
    "NONACC (FI)/ kakscub08/ BANASHANKARI19/ KA-BA",
    "NONACC (FI)/ kabacsl08/ BASAVANAGUDI/ KA-GN",
    "NONACC (FI)/ kabacsl08/ JP NAGAR21/ KA-SV",
    "NONACC (BK)/ kacrsfl08/ KENGERI22/ KA-BA",
    "NONACC (FI)/ kakscsa08/ MAGADI ROAD23/ KA-GN",
    "NONACC (FI)/ kacrsl08/ PEENYA/ KA-SV",
    "NONACC (FI)/ kagcsl08/ NELAMANGALA2/ KA-BA",
    "NONACC (FI)/ kakscub08/ DEVANAHALLI3/ KA-GN",
    "NONACC (FI)/ kakscsa08/ ATTIBELE4/ KA-SV",
    "NONACC (BK)/ kacrsfl08/ BOMMANAHALLI/ KA-BA",
    "NONACC (FI)/ kacrsl08/ HENNUR6/ KA-GN",
    "NONACC (FI)/ kacrsfl09/ KADUGODI7/ KA-SV",
    "NONACC (FI)/ kagcsl08/ KUNDALAHALLI8/ KA-BA",
    "NONACC (FI)/ kakscub08/ CV RAMAN NAGAR/ KA-GN",
    "NONACC (FI)/ kagcsl09/ RICHMOND TOWN10/ KA-SV",
    "NONACC (BK)/ kacrsl08/ FRAZER TOWN11/ KA-BA",
    "NONACC (FI)/ kaksfcl08/ RT NAGAR12/ KA-GN",
    "NONACC (FI)/ kagcsl09/ VIDYARANYAPURA/ KA-SV",
    "NONACC (FI)/ kaksfcl08/ BANASWADI14/ KA-BA",
    "NONACC (FI)/ kakscub08/ KASTURINAGAR15/ KA-GN",
    "NONACC (FI)/ kacrsl08/ KALASIPALYA16/ KA-SV",
    "NONACC (BK)/ kacrsfl09/ MYSORE ROAD/ KA-BA",
    "NONACC (FI)/ kagcsl08/ CHICKPET18/ KA-GN",
    "NONACC (FI)/ kakscub08/ ULSOOR19/ KA-SV",
    "NONACC (FI)/ kagcsl09/ SADASHIVANAGAR20/ KA-BA",
    "NONACC (FI)/ kabacsl08/ SANJAY NAGAR/ KA-GN",
    "NONACC (FI)/ kagcsl08/ JALAHALLI22/ KA-SV",
    "NONACC (BK)/ kagcsl08/ NANDINI LAYOUT23/ KA-BA",
    "NONACC (FI)/ kaksfcl08/ CHANDRA LAYOUT1/ KA-GN",
    "NONACC (FI)/ kakscub08/ BASAVESHWARANAGAR/ KA-SV",
    "NONACC (FI)/ kacrsl08/ KENGERI SATELLITE TOWN3/ KA-BA",
    "NONACC (FI)/ kakscub08/ HOSAKEREHALLI4/ KA-GN",
    "NONACC (FI)/ kagcsl09/ ANEKAL5/ KA-SV",
    "NONACC (BK)/ kagcsl08/ BIDADI/ KA-BA",
    "NONACC (FI)/ kakscub08/ RAMANAGARA7/ KA-GN",
    "NONACC (FI)/ kabacsl08/ KANAKAPURA8/ KA-SV",
    "NONACC (FI)/ kacrsfl08/ MANDYA ROAD9/ KA-BA",
    "NONACC (FI)/ kadopkc07/ MALLESHPALYA/ KA-GN",
    "NONACC (FI)/ kakscub08/ VIGNAN NAGAR11/ KA-SV",
    "NONACC (BK)/ kakscsa08/ MUNNEKOLALA12/ KA-BA",
    "NONACC (FI)/ kabacsl08/ PANATHUR13/ KA-GN",
    "NONACC (FI)/ kacrsfl08/ HARALUR/ KA-SV",
    "NONACC (FI)/ kagcsl08/ KODIGEHALLI15/ KA-BA",
    "NONACC (FI)/ kacrsl08/ VIDYAPEETA16/ KA-GN",
    "NONACC (FI)/ kagcsl08/ KAGGADASAPURA17/ KA-SV",
    "NONACC (BK)/ kacrsfl08/ NAGASANDRA/ KA-BA",
    "NONACC (FI)/ kadopkc07/ DASARAHALLI19/ KA-GN",
    "NONACC (FI)/ kaksfcl08/ YASHASWINI NAGAR20/ KA-SV",
    "NONACC (FI)/ kacrsfl08/ THANISANDRA21/ KA-BA",
    "NONACC (FI)/ kabacsl08/ JAKKUR/ KA-GN",
    "NONACC (FI)/ kaksfcl08/ CHIKKABANAVARA23/ KA-SV",
    "NONACC (BK)/ kadopkc07/ KONANAKUNTE1/ KA-BA",
    "NONACC (FI)/ kaksfcl08/ UTTARAHALLI2/ KA-GN",
    "NONACC (FI)/ kabacsl08/ SUBRAMANYAPURA/ KA-SV",
    "NONACC (FI)/ kakscsa08/ GIRINAGAR4/ KA-BA",
    "NONACC (FI)/ kacrsfl08/ KUMARASWAMY LAYOUT5/ KA-GN",
    "NONACC (FI)/ kabacsl08/ RR NAGAR6/ KA-SV",
    "NONACC (BK)/ kacrsl08/ BILEKAHALLI/ KA-BA",
    "NONACC (FI)/ kacrsfl09/ HULIMAVU8/ KA-GN",
    "NONACC (FI)/ kadopkc07/ AKSHAYANAGAR9/ KA-SV",
    "NONACC (FI)/ kabacsl08/ BEGUR10/ KA-BA",
    "NONACC (FI)/ kakscub08/ SINGASANDRA/ KA-GN",
    "NONACC (FI)/ kagcsl09/ PARAPPANA AGRAHARA12/ KA-SV",
    "NONACC (BK)/ kabacsl08/ HONGASANDRA13/ KA-BA",
    "NONACC (FI)/ kakscub08/ KAMAKSHIPALYA14/ KA-GN",
    "NONACC (FI)/ kagcsl08/ LAGGERE/ KA-SV",
    "NONACC (FI)/ kacrsl08/ BYATARAYANAPURA16/ KA-BA",
    "NONACC (FI)/ kagcsl09/ DODDABALLAPUR17/ KA-GN",
    "NONACC (FI)/ kacrsfl09/ MADANAYAKANAHALLI18/ KA-SV",
    "NONACC (BK)/ kaksfcl08/ KUMBALGODU/ KA-BA",
    "NONACC (FI)/ kadopkc07/ VIRGONAGAR20/ KA-GN",
    "NONACC (FI)/ kakscsa08/ MEDAHALLI21/ KA-SV",
    "NONACC (FI)/ kacrsfl08/ KR PURAM22/ KA-BA",
    "NONACC (FI)/ kacrsfl09/ SEEGEHALLI/ KA-GN",
    "NONACC (FI)/ kacrsfl09/ AVALAHALLI1/ KA-SV",
    "NONACC (BK)/ kagcsl08/ KOTHANUR2/ KA-BA",
    "NONACC (FI)/ kakscsa08/ GOTTIGERE3/ KA-GN",
    "NONACC (FI)/ kabacsl08/ CHIKKALLASANDRA/ KA-SV",
    "NONACC (FI)/ kagcsl08/ WHITEFIELD5/ KA-BA",
    "NONACC (FI)/ kagcsl09/ SARJAPUR6/ KA-GN",
    "NONACC (FI)/ kakscsa08/ ELECTRONIC CITY7/ KA-SV",
    "NONACC (BK)/ kacrsfl09/ HEBBAL/ KA-BA",
    "NONACC (FI)/ kagcsl09/ BANASHANKARI9/ KA-GN",
    "NONACC (FI)/ kacrsl08/ BASAVANAGUDI10/ KA-SV",
    "NONACC (FI)/ kaksfcl08/ JP NAGAR11/ KA-BA",
    "NONACC (FI)/ kacrsfl09/ KENGERI/ KA-GN",
    "NONACC (FI)/ kakscsa08/ MAGADI ROAD13/ KA-SV",
    "NONACC (BK)/ kacrsl08/ PEENYA14/ KA-BA",
    "NONACC (FI)/ kacrsfl09/ NELAMANGALA15/ KA-GN",
    "NONACC (FI)/ kacrsl08/ DEVANAHALLI/ KA-SV",
    "NONACC (FI)/ kadopkc07/ ATTIBELE17/ KA-BA",
    "NONACC (FI)/ kacrsfl08/ BOMMANAHALLI18/ KA-GN",
    "NONACC (FI)/ kacrsl08/ HENNUR19/ KA-SV",
    "NONACC (BK)/ kacrsfl09/ KADUGODI/ KA-BA",
    "NONACC (FI)/ kagcsl08/ KUNDALAHALLI21/ KA-GN",
    "NONACC (FI)/ kacrsfl08/ CV RAMAN NAGAR22/ KA-SV",
    "NONACC (FI)/ kakscsa08/ RICHMOND TOWN23/ KA-BA",
    "NONACC (FI)/ kacrsfl09/ FRAZER TOWN/ KA-GN",
    "NONACC (FI)/ kakscsa08/ RT NAGAR2/ KA-SV",
    "NONACC (BK)/ kakscsa08/ VIDYARANYAPURA3/ KA-BA",
    "NONACC (FI)/ kaksfcl08/ BANASWADI4/ KA-GN",
    "NONACC (FI)/ kagcsl08/ KASTURINAGAR/ KA-SV",
    "NONACC (FI)/ kacrsfl09/ KALASIPALYA6/ KA-BA",
    "NONACC (FI)/ kadopkc07/ MYSORE ROAD7/ KA-GN",
    "NONACC (FI)/ kacrsfl09/ CHICKPET8/ KA-SV",
    "NONACC (BK)/ kacrsfl08/ ULSOOR/ KA-BA",
    "NONACC (FI)/ kacrsl08/ SADASHIVANAGAR10/ KA-GN",
    "NONACC (FI)/ kagcsl09/ SANJAY NAGAR11/ KA-SV",
    "NONACC (FI)/ kakscsa08/ JALAHALLI12/ KA-BA",
    "NONACC (FI)/ kagcsl08/ NANDINI LAYOUT/ KA-GN",
    "NONACC (FI)/ kakscub08/ CHANDRA LAYOUT14/ KA-SV",
    "NONACC (BK)/ kacrsfl09/ BASAVESHWARANAGAR15/ KA-BA",
    "NONACC (FI)/ kakscub08/ KENGERI SATELLITE TOWN16/ KA-GN",
    "NONACC (FI)/ kagcsl09/ HOSAKEREHALLI/ KA-SV",
    "NONACC (FI)/ kakscsa08/ ANEKAL18/ KA-BA",
    "NONACC (FI)/ kacrsl08/ BIDADI19/ KA-GN",
    "NONACC (FI)/ kagcsl09/ RAMANAGARA20/ KA-SV",
    "NONACC (BK)/ kagcsl08/ KANAKAPURA/ KA-BA",
    "NONACC (FI)/ kaksfcl08/ MANDYA ROAD22/ KA-GN",
    "NONACC (FI)/ kacrsl08/ MALLESHPALYA23/ KA-SV",
    "NONACC (FI)/ kakscub08/ VIGNAN NAGAR1/ KA-BA",
    "NONACC (FI)/ kakscsa08/ MUNNEKOLALA/ KA-GN",
    "NONACC (FI)/ kakscub08/ PANATHUR3/ KA-SV",
    "NONACC (BK)/ kacrsl08/ HARALUR4/ KA-BA",
    "NONACC (FI)/ kagcsl08/ KODIGEHALLI5/ KA-GN",
    "NONACC (FI)/ kaksfcl08/ VIDYAPEETA/ KA-SV",
    "NONACC (FI)/ kacrsfl08/ KAGGADASAPURA7/ KA-BA",
    "NONACC (FI)/ kabacsl08/ NAGASANDRA8/ KA-GN",
    "NONACC (FI)/ kacrsl08/ DASARAHALLI9/ KA-SV",
    "NONACC (BK)/ kacrsfl09/ YASHASWINI NAGAR/ KA-BA",
    "NONACC (FI)/ kacrsfl09/ THANISANDRA11/ KA-GN",
    "NONACC (FI)/ kacrsl08/ JAKKUR12/ KA-SV",
    "NONACC (FI)/ kadopkc07/ CHIKKABANAVARA13/ KA-BA",
    "NONACC (FI)/ kagcsl08/ KONANAKUNTE/ KA-GN",
    "NONACC (FI)/ kacrsfl08/ UTTARAHALLI15/ KA-SV",
    "NONACC (BK)/ kadopkc07/ SUBRAMANYAPURA16/ KA-BA",
    "NONACC (FI)/ kaksfcl08/ GIRINAGAR17/ KA-GN",
    "NONACC (FI)/ kabacsl08/ KUMARASWAMY LAYOUT/ KA-SV",
    "NONACC (FI)/ kakscub08/ RR NAGAR19/ KA-BA",
    "NONACC (FI)/ kacrsfl08/ BILEKAHALLI20/ KA-GN",
    "NONACC (FI)/ kakscsa08/ HULIMAVU21/ KA-SV",
    "NONACC (BK)/ kacrsfl09/ AKSHAYANAGAR/ KA-BA",
    "NONACC (FI)/ kabacsl08/ BEGUR23/ KA-GN",
    "NONACC (FI)/ kagcsl09/ SINGASANDRA1/ KA-SV",
    "NONACC (FI)/ kagcsl09/ PARAPPANA AGRAHARA2/ KA-BA",
    "NONACC (FI)/ kacrsl08/ HONGASANDRA/ KA-GN",
    "NONACC (FI)/ kadopkc07/ KAMAKSHIPALYA4/ KA-SV",
    "NONACC (BK)/ kagcsl09/ LAGGERE5/ KA-BA",
    "NONACC (FI)/ kabacsl08/ BYATARAYANAPURA6/ KA-GN",
    "NONACC (FI)/ kakscsa08/ DODDABALLAPUR/ KA-SV",
    "NONACC (FI)/ kakscsa08/ MADANAYAKANAHALLI8/ KA-BA",
    "NONACC (FI)/ kacrsl08/ KUMBALGODU9/ KA-GN",
    "NONACC (FI)/ kagcsl08/ VIRGONAGAR10/ KA-SV",
    "NONACC (BK)/ kabacsl08/ MEDAHALLI/ KA-BA",
    "NONACC (FI)/ kagcsl08/ KR PURAM12/ KA-GN",
    "NONACC (FI)/ kaksfcl08/ SEEGEHALLI13/ KA-SV",
    "NONACC (FI)/ kakscsa08/ AVALAHALLI14/ KA-BA",
    "NONACC (FI)/ kakscub08/ KOTHANUR/ KA-GN",
    "NONACC (FI)/ kadopkc07/ GOTTIGERE16/ KA-SV",
    "NONACC (BK)/ kacrsfl08/ CHIKKALLASANDRA17/ KA-BA",
    "NONACC (FI)/ kagcsl08/ WHITEFIELD18/ KA-GN",
    "NONACC (FI)/ kagcsl08/ SARJAPUR/ KA-SV",
    "NONACC (FI)/ kakscub08/ ELECTRONIC CITY20/ KA-BA",
    "NONACC (FI)/ kadopkc07/ HEBBAL21/ KA-GN",
    "NONACC (FI)/ kagcsl08/ BANASHANKARI22/ KA-SV",
    "NONACC (BK)/ kacrsl08/ BASAVANAGUDI/ KA-BA",
    "NONACC (FI)/ kaksfcl08/ JP NAGAR1/ KA-GN",
    "NONACC (FI)/ kabacsl08/ KENGERI2/ KA-SV",
    "NONACC (FI)/ kacrsl08/ MAGADI ROAD3/ KA-BA",
    "NONACC (FI)/ kabacsl08/ PEENYA/ KA-GN",
    "NONACC (FI)/ kacrsl08/ NELAMANGALA5/ KA-SV",
    "NONACC (BK)/ kacrsl08/ DEVANAHALLI6/ KA-BA",
    "NONACC (FI)/ kagcsl08/ ATTIBELE7/ KA-GN",
    "NONACC (FI)/ kagcsl09/ BOMMANAHALLI/ KA-SV",
    "NONACC (FI)/ kaksfcl08/ HENNUR9/ KA-BA",
    "NONACC (FI)/ kakscub08/ KADUGODI10/ KA-GN",
    "NONACC (FI)/ kaksfcl08/ KUNDALAHALLI11/ KA-SV",
    "NONACC (BK)/ kaksfcl08/ CV RAMAN NAGAR/ KA-BA",
    "NONACC (FI)/ kagcsl09/ RICHMOND TOWN13/ KA-GN",
    "NONACC (FI)/ kadopkc07/ FRAZER TOWN14/ KA-SV",
    "NONACC (FI)/ kacrsfl08/ RT NAGAR15/ KA-BA",
    "NONACC (FI)/ kagcsl09/ VIDYARANYAPURA/ KA-GN",
    "NONACC (FI)/ kakscub08/ BANASWADI17/ KA-SV",
    "NONACC (BK)/ kakscsa08/ KASTURINAGAR18/ KA-BA",
    "NONACC (FI)/ kakscub08/ KALASIPALYA19/ KA-GN",
    "NONACC (FI)/ kagcsl09/ MYSORE ROAD/ KA-SV",
    "NONACC (FI)/ kabacsl08/ CHICKPET21/ KA-BA",
    "NONACC (FI)/ kacrsl08/ ULSOOR22/ KA-GN",
    "NONACC (FI)/ kadopkc07/ SADASHIVANAGAR23/ KA-SV",
    "NONACC (BK)/ kacrsl08/ SANJAY NAGAR/ KA-BA",
    "NONACC (FI)/ kacrsfl09/ JALAHALLI2/ KA-GN",
    "NONACC (FI)/ kabacsl08/ NANDINI LAYOUT3/ KA-SV",
    "NONACC (FI)/ kabacsl08/ CHANDRA LAYOUT4/ KA-BA",
    "NONACC (FI)/ kagcsl09/ BASAVESHWARANAGAR/ KA-GN",
    "NONACC (FI)/ kacrsl08/ KENGERI SATELLITE TOWN6/ KA-SV",
    "NONACC (BK)/ kadopkc07/ HOSAKEREHALLI7/ KA-BA",
    "NONACC (FI)/ kakscub08/ ANEKAL8/ KA-GN",
    "NONACC (FI)/ kaksfcl08/ BIDADI/ KA-SV",
    "NONACC (FI)/ kaksfcl08/ RAMANAGARA10/ KA-BA",
    "NONACC (FI)/ kadopkc07/ KANAKAPURA11/ KA-GN",
    "NONACC (FI)/ kagcsl09/ MANDYA ROAD12/ KA-SV",
    "NONACC (BK)/ kakscsa08/ MALLESHPALYA/ KA-BA",
    "NONACC (FI)/ kabacsl08/ VIGNAN NAGAR14/ KA-GN",
    "NONACC (FI)/ kakscsa08/ MUNNEKOLALA15/ KA-SV",
    "NONACC (FI)/ kabacsl08/ PANATHUR16/ KA-BA",
    "NONACC (FI)/ kakscub08/ HARALUR/ KA-GN",
    "NONACC (FI)/ kakscsa08/ KODIGEHALLI18/ KA-SV",
    "NONACC (BK)/ kakscsa08/ VIDYAPEETA19/ KA-BA",
    "NONACC (FI)/ kakscub08/ KAGGADASAPURA20/ KA-GN",
    "NONACC (FI)/ kacrsl08/ NAGASANDRA/ KA-SV",
    "NONACC (FI)/ kabacsl08/ DASARAHALLI22/ KA-BA",
    "NONACC (FI)/ kabacsl08/ YASHASWINI NAGAR23/ KA-GN",
    "NONACC (FI)/ kadopkc07/ THANISANDRA1/ KA-SV",
    "NONACC (BK)/ kagcsl09/ JAKKUR/ KA-BA",
    "NONACC (FI)/ kadopkc07/ CHIKKABANAVARA3/ KA-GN",
    "NONACC (FI)/ kacrsfl09/ KONANAKUNTE4/ KA-SV",
    "NONACC (FI)/ kaksfcl08/ UTTARAHALLI5/ KA-BA",
    "NONACC (FI)/ kaksfcl08/ SUBRAMANYAPURA/ KA-GN",
    "NONACC (FI)/ kaksfcl08/ GIRINAGAR7/ KA-SV",
    "NONACC (BK)/ kagcsl09/ KUMARASWAMY LAYOUT8/ KA-BA",
    "NONACC (FI)/ kagcsl08/ RR NAGAR9/ KA-GN",
    "NONACC (FI)/ kacrsfl09/ BILEKAHALLI/ KA-SV",
    "NONACC (FI)/ kacrsfl09/ HULIMAVU11/ KA-BA",
    "NONACC (FI)/ kaksfcl08/ AKSHAYANAGAR12/ KA-GN",
    "NONACC (FI)/ kabacsl08/ BEGUR13/ KA-SV",
    "NONACC (BK)/ kadopkc07/ SINGASANDRA/ KA-BA",
    "NONACC (FI)/ kadopkc07/ PARAPPANA AGRAHARA15/ KA-GN",
    "NONACC (FI)/ kagcsl09/ HONGASANDRA16/ KA-SV",
    "NONACC (FI)/ kabacsl08/ KAMAKSHIPALYA17/ KA-BA",
    "NONACC (FI)/ kacrsfl08/ LAGGERE/ KA-GN",
    "NONACC (FI)/ kakscub08/ BYATARAYANAPURA19/ KA-SV",
    "NONACC (BK)/ kabacsl08/ DODDABALLAPUR20/ KA-BA",
    "NONACC (FI)/ kacrsfl09/ MADANAYAKANAHALLI21/ KA-GN",
    "NONACC (FI)/ kacrsfl09/ KUMBALGODU/ KA-SV",
    "NONACC (FI)/ kacrsfl08/ VIRGONAGAR23/ KA-BA",
    "NONACC (FI)/ kacrsfl09/ MEDAHALLI1/ KA-GN",
    "NONACC (FI)/ kabacsl08/ KR PURAM2/ KA-SV",
    "NONACC (BK)/ kadopkc07/ SEEGEHALLI/ KA-BA",
    "NONACC (FI)/ kakscub08/ AVALAHALLI4/ KA-GN",
    "NONACC (FI)/ kacrsfl08/ KOTHANUR5/ KA-SV",
    "NONACC (FI)/ kacrsfl09/ GOTTIGERE6/ KA-BA",
    "NONACC (FI)/ kaksfcl08/ CHIKKALLASANDRA/ KA-GN",
    "NONACC (FI)/ kacrsfl09/ WHITEFIELD8/ KA-SV",
    "NONACC (BK)/ kaksfcl08/ SARJAPUR9/ KA-BA",
    "NONACC (FI)/ kadopkc07/ ELECTRONIC CITY10/ KA-GN",
    "NONACC (FI)/ kaksfcl08/ HEBBAL/ KA-SV",
    "NONACC (FI)/ kakscub08/ BANASHANKARI12/ KA-BA",
    "NONACC (FI)/ kagcsl09/ BASAVANAGUDI13/ KA-GN",
    "NONACC (FI)/ kacrsfl08/ JP NAGAR14/ KA-SV",
    "NONACC (BK)/ kagcsl09/ KENGERI/ KA-BA",
    "NONACC (FI)/ kagcsl08/ MAGADI ROAD16/ KA-GN",
    "NONACC (FI)/ kagcsl09/ PEENYA17/ KA-SV",
    "NONACC (FI)/ kakscsa08/ NELAMANGALA18/ KA-BA",
    "NONACC (FI)/ kacrsfl08/ DEVANAHALLI/ KA-GN",
    "NONACC (FI)/ kabacsl08/ ATTIBELE20/ KA-SV",
    "NONACC (BK)/ kacrsfl08/ BOMMANAHALLI21/ KA-BA",
    "NONACC (FI)/ kakscsa08/ HENNUR22/ KA-GN",
    "NONACC (FI)/ kakscub08/ KADUGODI/ KA-SV",
    "NONACC (FI)/ kacrsl08/ KUNDALAHALLI1/ KA-BA",
    "NONACC (FI)/ kacrsl08/ CV RAMAN NAGAR2/ KA-GN",
    "NONACC (FI)/ kabacsl08/ RICHMOND TOWN3/ KA-SV",
    "NONACC (BK)/ kacrsfl08/ FRAZER TOWN/ KA-BA",
    "NONACC (FI)/ kakscsa08/ RT NAGAR5/ KA-GN",
    "NONACC (FI)/ kacrsl08/ VIDYARANYAPURA6/ KA-SV",
    "NONACC (FI)/ kacrsl08/ BANASWADI7/ KA-BA",
    "NONACC (FI)/ kacrsfl09/ KASTURINAGAR/ KA-GN",
    "NONACC (FI)/ kadopkc07/ KALASIPALYA9/ KA-SV",
    "NONACC (BK)/ kacrsl08/ MYSORE ROAD10/ KA-BA",
    "NONACC (FI)/ kagcsl09/ CHICKPET11/ KA-GN",
    "NONACC (FI)/ kadopkc07/ ULSOOR/ KA-SV",
    "NONACC (FI)/ kabacsl08/ SADASHIVANAGAR13/ KA-BA",
    "NONACC (FI)/ kaksfcl08/ SANJAY NAGAR14/ KA-GN",
    "NONACC (FI)/ kacrsfl09/ JALAHALLI15/ KA-SV",
    "NONACC (BK)/ kacrsfl09/ NANDINI LAYOUT/ KA-BA",
    "NONACC (FI)/ kabacsl08/ CHANDRA LAYOUT17/ KA-GN",
    "NONACC (FI)/ kaksfcl08/ BASAVESHWARANAGAR18/ KA-SV",
    "NONACC (FI)/ kakscsa08/ KENGERI SATELLITE TOWN19/ KA-BA",
    "NONACC (FI)/ kacrsl08/ HOSAKEREHALLI/ KA-GN",
    "NONACC (FI)/ kakscub08/ ANEKAL21/ KA-SV",
    "NONACC (BK)/ kacrsfl08/ BIDADI22/ KA-BA",
    "NONACC (FI)/ kacrsl08/ RAMANAGARA23/ KA-GN",
    "NONACC (FI)/ kadopkc07/ KANAKAPURA/ KA-SV",
    "NONACC (FI)/ kacrsfl08/ MANDYA ROAD2/ KA-BA",
    "NONACC (FI)/ kabacsl08/ MALLESHPALYA3/ KA-GN",
    "NONACC (FI)/ kacrsfl09/ VIGNAN NAGAR4/ KA-SV",
    "NONACC (BK)/ kakscsa08/ MUNNEKOLALA/ KA-BA",
    "NONACC (FI)/ kabacsl08/ PANATHUR6/ KA-GN",
    "NONACC (FI)/ kakscsa08/ HARALUR7/ KA-SV",
    "NONACC (FI)/ kacrsfl08/ KODIGEHALLI8/ KA-BA",
    "NONACC (FI)/ kacrsfl09/ VIDYAPEETA/ KA-GN",
    "NONACC (FI)/ kakscub08/ KAGGADASAPURA10/ KA-SV",
    "NONACC (BK)/ kabacsl08/ NAGASANDRA11/ KA-BA",
    "NONACC (FI)/ kagcsl08/ DASARAHALLI12/ KA-GN",
    "NONACC (FI)/ kacrsfl08/ YASHASWINI NAGAR/ KA-SV",
    "NONACC (FI)/ kacrsfl08/ THANISANDRA14/ KA-BA",
    "NONACC (FI)/ kacrsfl08/ JAKKUR15/ KA-GN",
    "NONACC (FI)/ kakscsa08/ CHIKKABANAVARA16/ KA-SV",
    "NONACC (BK)/ kaksfcl08/ KONANAKUNTE/ KA-BA",
    "NONACC (FI)/ kagcsl08/ UTTARAHALLI18/ KA-GN",
    "NONACC (FI)/ kakscub08/ SUBRAMANYAPURA19/ KA-SV",
    "NONACC (FI)/ kacrsfl08/ GIRINAGAR20/ KA-BA",
    "NONACC (FI)/ kakscsa08/ KUMARASWAMY LAYOUT/ KA-GN",
    "NONACC (FI)/ kacrsl08/ RR NAGAR22/ KA-SV",
    "NONACC (BK)/ kabacsl08/ BILEKAHALLI23/ KA-BA",
    "NONACC (FI)/ kakscsa08/ HULIMAVU1/ KA-GN",
    "NONACC (FI)/ kakscub08/ AKSHAYANAGAR/ KA-SV",
    "NONACC (FI)/ kakscsa08/ BEGUR3/ KA-BA",
    "NONACC (FI)/ kakscsa08/ SINGASANDRA4/ KA-GN",
    "NONACC (FI)/ kakscsa08/ PARAPPANA AGRAHARA5/ KA-SV",
    "NONACC (BK)/ kakscub08/ HONGASANDRA/ KA-BA",
    "NONACC (FI)/ kacrsfl08/ KAMAKSHIPALYA7/ KA-GN",
    "NONACC (FI)/ kakscub08/ LAGGERE8/ KA-SV",
    "NONACC (FI)/ kabacsl08/ BYATARAYANAPURA9/ KA-BA",
    "NONACC (FI)/ kacrsfl09/ DODDABALLAPUR/ KA-GN",
    "NONACC (FI)/ kagcsl08/ MADANAYAKANAHALLI11/ KA-SV",
    "NONACC (BK)/ kacrsfl09/ KUMBALGODU12/ KA-BA",
    "NONACC (FI)/ kagcsl08/ VIRGONAGAR13/ KA-GN",
    "NONACC (FI)/ kabacsl08/ MEDAHALLI/ KA-SV",
    "NONACC (FI)/ kaksfcl08/ KR PURAM15/ KA-BA",
    "NONACC (FI)/ kadopkc07/ SEEGEHALLI16/ KA-GN",
    "NONACC (FI)/ kadopkc07/ AVALAHALLI17/ KA-SV",
    "NONACC (BK)/ kabacsl08/ KOTHANUR/ KA-BA",
    "NONACC (FI)/ kacrsl08/ GOTTIGERE19/ KA-GN",
    "NONACC (FI)/ kacrsfl09/ CHIKKALLASANDRA20/ KA-SV",
    "NONACC (FI)/ kakscsa08/ WHITEFIELD21/ KA-BA",
    "NONACC (FI)/ kabacsl08/ SARJAPUR/ KA-GN",
    "NONACC (FI)/ kacrsl08/ ELECTRONIC CITY23/ KA-SV",
    "NONACC (BK)/ kacrsfl08/ HEBBAL1/ KA-BA",
    "NONACC (FI)/ kaksfcl08/ BANASHANKARI2/ KA-GN",
    "NONACC (FI)/ kadopkc07/ BASAVANAGUDI/ KA-SV",
    "NONACC (FI)/ kadopkc07/ JP NAGAR4/ KA-BA",
    "NONACC (FI)/ kabacsl08/ KENGERI5/ KA-GN",
    "NONACC (FI)/ kakscsa08/ MAGADI ROAD6/ KA-SV",
    "NONACC (BK)/ kagcsl09/ PEENYA/ KA-BA",
    "NONACC (FI)/ kacrsfl08/ NELAMANGALA8/ KA-GN",
    "NONACC (FI)/ kaksfcl08/ DEVANAHALLI9/ KA-SV",
    "NONACC (FI)/ kacrsfl08/ ATTIBELE10/ KA-BA",
    "NONACC (FI)/ kagcsl09/ BOMMANAHALLI/ KA-GN",
    "NONACC (FI)/ kakscsa08/ HENNUR12/ KA-SV",
    "NONACC (BK)/ kacrsl08/ KADUGODI13/ KA-BA",
    "NONACC (FI)/ kaksfcl08/ KUNDALAHALLI14/ KA-GN",
    "NONACC (FI)/ kadopkc07/ CV RAMAN NAGAR/ KA-SV",
    "NONACC (FI)/ kakscsa08/ RICHMOND TOWN16/ KA-BA",
    "NONACC (FI)/ kagcsl09/ FRAZER TOWN17/ KA-GN",
    "NONACC (FI)/ kabacsl08/ RT NAGAR18/ KA-SV",
    "NONACC (BK)/ kacrsfl08/ VIDYARANYAPURA/ KA-BA",
    "NONACC (FI)/ kakscub08/ BANASWADI20/ KA-GN",
    "NONACC (FI)/ kacrsl08/ KASTURINAGAR21/ KA-SV",
    "NONACC (FI)/ kaksfcl08/ KALASIPALYA22/ KA-BA",
    "NONACC (FI)/ kacrsfl09/ MYSORE ROAD/ KA-GN",
    "NONACC (FI)/ kacrsfl09/ CHICKPET1/ KA-SV",
    "NONACC (BK)/ kacrsfl08/ ULSOOR2/ KA-BA",
    "NONACC (FI)/ kabacsl08/ SADASHIVANAGAR3/ KA-GN",
    "NONACC (FI)/ kacrsfl08/ SANJAY NAGAR/ KA-SV",
    "NONACC (FI)/ kagcsl08/ JALAHALLI5/ KA-BA",
    "NONACC (FI)/ kakscub08/ NANDINI LAYOUT6/ KA-GN",
    "NONACC (FI)/ kaksfcl08/ CHANDRA LAYOUT7/ KA-SV",
    "NONACC (BK)/ kacrsfl08/ BASAVESHWARANAGAR/ KA-BA",
    "NONACC (FI)/ kagcsl09/ KENGERI SATELLITE TOWN9/ KA-GN",
    "NONACC (FI)/ kagcsl08/ HOSAKEREHALLI10/ KA-SV",
    "NONACC (FI)/ kagcsl09/ ANEKAL11/ KA-BA",
    "NONACC (FI)/ kakscub08/ BIDADI/ KA-GN",
    "NONACC (FI)/ kabacsl08/ RAMANAGARA13/ KA-SV",
    "NONACC (BK)/ kagcsl08/ KANAKAPURA14/ KA-BA",
    "NONACC (FI)/ kacrsl08/ MANDYA ROAD15/ KA-GN",
    "NONACC (FI)/ kaksfcl08/ MALLESHPALYA/ KA-SV",
    "NONACC (FI)/ kabacsl08/ VIGNAN NAGAR17/ KA-BA",
    "NONACC (FI)/ kabacsl08/ MUNNEKOLALA18/ KA-GN",
    "NONACC (FI)/ kabacsl08/ PANATHUR19/ KA-SV",
    "NONACC (BK)/ kaksfcl08/ HARALUR/ KA-BA",
    "NONACC (FI)/ kaksfcl08/ KODIGEHALLI21/ KA-GN",
    "NONACC (FI)/ kakscsa08/ VIDYAPEETA22/ KA-SV",
    "NONACC (FI)/ kacrsfl08/ KAGGADASAPURA23/ KA-BA",
    "NONACC (FI)/ kaksfcl08/ NAGASANDRA/ KA-GN",
    "NONACC (FI)/ kabacsl08/ DASARAHALLI2/ KA-SV",
    "NONACC (BK)/ kadopkc07/ YASHASWINI NAGAR3/ KA-BA",
    "NONACC (FI)/ kakscsa08/ THANISANDRA4/ KA-GN",
    "NONACC (FI)/ kakscsa08/ JAKKUR/ KA-SV",
    "NONACC (FI)/ kakscub08/ CHIKKABANAVARA6/ KA-BA",
    "NONACC (FI)/ kakscsa08/ KONANAKUNTE7/ KA-GN",
    "NONACC (FI)/ kacrsl08/ UTTARAHALLI8/ KA-SV",
    "NONACC (BK)/ kagcsl08/ SUBRAMANYAPURA/ KA-BA",
    "NONACC (FI)/ kabacsl08/ GIRINAGAR10/ KA-GN",
    "NONACC (FI)/ kakscub08/ KUMARASWAMY LAYOUT11/ KA-SV",
    "NONACC (FI)/ kakscub08/ RR NAGAR12/ KA-BA",
    "NONACC (FI)/ kaksfcl08/ BILEKAHALLI/ KA-GN",
    "NONACC (FI)/ kagcsl09/ HULIMAVU14/ KA-SV",
    "NONACC (BK)/ kagcsl08/ AKSHAYANAGAR15/ KA-BA",
    "NONACC (FI)/ kagcsl08/ BEGUR16/ KA-GN",
    "NONACC (FI)/ kagcsl09/ SINGASANDRA/ KA-SV",
    "NONACC (FI)/ kabacsl08/ PARAPPANA AGRAHARA18/ KA-BA",
    "NONACC (FI)/ kagcsl08/ HONGASANDRA19/ KA-GN",
    "NONACC (FI)/ kakscub08/ KAMAKSHIPALYA20/ KA-SV",
    "NONACC (BK)/ kagcsl08/ LAGGERE/ KA-BA",
    "NONACC (FI)/ kadopkc07/ BYATARAYANAPURA22/ KA-GN",
    "NONACC (FI)/ kakscsa08/ DODDABALLAPUR23/ KA-SV",
    "NONACC (FI)/ kaksfcl08/ MADANAYAKANAHALLI1/ KA-BA",
    "NONACC (FI)/ kacrsl08/ KUMBALGODU/ KA-GN",
    "NONACC (FI)/ kaksfcl08/ VIRGONAGAR3/ KA-SV",
    "NONACC (BK)/ kakscsa08/ MEDAHALLI4/ KA-BA",
    "NONACC (FI)/ kacrsfl09/ KR PURAM5/ KA-GN",
    "NONACC (FI)/ kacrsfl08/ SEEGEHALLI/ KA-SV",
    "NONACC (FI)/ kagcsl08/ AVALAHALLI7/ KA-BA",
    "NONACC (FI)/ kakscub08/ KOTHANUR8/ KA-GN",
    "NONACC (FI)/ kagcsl09/ GOTTIGERE9/ KA-SV",
    "NONACC (BK)/ kagcsl08/ CHIKKALLASANDRA/ KA-BA",
    "NONACC (FI)/ kacrsfl09/ WHITEFIELD11/ KA-GN",
    "NONACC (FI)/ kagcsl08/ SARJAPUR12/ KA-SV",
    "NONACC (FI)/ kacrsfl09/ ELECTRONIC CITY13/ KA-BA",
    "NONACC (FI)/ kacrsfl08/ HEBBAL/ KA-GN",
    "NONACC (FI)/ kaksfcl08/ BANASHANKARI15/ KA-SV",
    "NONACC (BK)/ kacrsfl08/ BASAVANAGUDI16/ KA-BA",
    "NONACC (FI)/ kagcsl09/ JP NAGAR17/ KA-GN",
    "NONACC (FI)/ kagcsl09/ MAGADI ROAD19/ KA-BA",
    "NONACC (FI)/ kagcsl08/ PEENYA20/ KA-GN",
    "NONACC (FI)/ kakscub08/ NELAMANGALA21/ KA-SV",
    "NONACC (BK)/ kakscub08/ DEVANAHALLI/ KA-BA",
    "NONACC (FI)/ kacrsl08/ ATTIBELE23/ KA-GN",
    "NONACC (FI)/ kacrsfl09/ BOMMANAHALLI1/ KA-SV",
    "NONACC (FI)/ kacrsfl09/ HENNUR2/ KA-BA",
    "NONACC (FI)/ kakscsa08/ KADUGODI/ KA-GN",
    "NONACC (FI)/ kagcsl09/ KUNDALAHALLI4/ KA-SV",
    "NONACC (BK)/ kacrsfl08/ CV RAMAN NAGAR5/ KA-BA",
    "NONACC (FI)/ kadopkc07/ RICHMOND TOWN6/ KA-GN",
    "NONACC (FI)/ kabacsl08/ FRAZER TOWN/ KA-SV",
    "NONACC (FI)/ kakscub08/ RT NAGAR8/ KA-BA",
    "NONACC (FI)/ kacrsfl08/ VIDYARANYAPURA9/ KA-GN",
    "NONACC (FI)/ kagcsl08/ BANASWADI10/ KA-SV",
    "NONACC (BK)/ kadopkc07/ KASTURINAGAR/ KA-BA",
    "NONACC (FI)/ kacrsl08/ KALASIPALYA12/ KA-GN",
    "NONACC (FI)/ kagcsl09/ MYSORE ROAD13/ KA-SV",
    "NONACC (FI)/ kabacsl08/ CHICKPET14/ KA-BA",
    "NONACC (FI)/ kadopkc07/ ULSOOR/ KA-GN",
    "NONACC (FI)/ kakscsa08/ SADASHIVANAGAR16/ KA-SV",
    "NONACC (BK)/ kacrsl08/ SANJAY NAGAR17/ KA-BA",
    "NONACC (FI)/ kadopkc07/ JALAHALLI18/ KA-GN",
    "NONACC (FI)/ kacrsl08/ CHANDRA LAYOUT20/ KA-BA",
    "NONACC (FI)/ kakscub08/ BASAVESHWARANAGAR21/ KA-GN",
    "NONACC (FI)/ kadopkc07/ KENGERI SATELLITE TOWN22/ KA-SV",
    "NONACC (BK)/ kacrsl08/ HOSAKEREHALLI/ KA-BA",
    "NONACC (FI)/ kagcsl08/ ANEKAL1/ KA-GN",
    "NONACC (FI)/ kagcsl09/ BIDADI2/ KA-SV",
    "NONACC (FI)/ kadopkc07/ RAMANAGARA3/ KA-BA",
    "NONACC (FI)/ kakscsa08/ KANAKAPURA/ KA-GN",
    "NONACC (FI)/ kakscsa08/ MANDYA ROAD5/ KA-SV",
    "NONACC (BK)/ kacrsfl09/ MALLESHPALYA6/ KA-BA",
    "NONACC (FI)/ kagcsl08/ VIGNAN NAGAR7/ KA-GN",
    "NONACC (FI)/ kagcsl08/ MUNNEKOLALA/ KA-SV",
    "NONACC (FI)/ kacrsfl08/ PANATHUR9/ KA-BA",
    "NONACC (FI)/ kacrsfl09/ HARALUR10/ KA-GN",
    "NONACC (FI)/ kagcsl08/ KODIGEHALLI11/ KA-SV",
    "NONACC (BK)/ kacrsl08/ VIDYAPEETA/ KA-BA",
    "NONACC (FI)/ kagcsl08/ KAGGADASAPURA13/ KA-GN",
    "NONACC (FI)/ kacrsl08/ NAGASANDRA14/ KA-SV",
    "NONACC (FI)/ kaksfcl08/ DASARAHALLI15/ KA-BA",
    "NONACC (FI)/ kabacsl08/ YASHASWINI NAGAR/ KA-GN",
    "NONACC (FI)/ kagcsl09/ THANISANDRA17/ KA-SV",
    "NONACC (BK)/ kabacsl08/ JAKKUR18/ KA-BA",
    "NONACC (FI)/ kadopkc07/ CHIKKABANAVARA19/ KA-GN",
    "NONACC (FI)/ kaksfcl08/ KONANAKUNTE/ KA-SV",
    "NONACC (FI)/ kacrsfl08/ UTTARAHALLI21/ KA-BA",
    "NONACC (FI)/ kacrsl08/ SUBRAMANYAPURA22/ KA-GN",
    "NONACC (FI)/ kacrsfl09/ GIRINAGAR23/ KA-SV",
    "NONACC (BK)/ kacrsfl08/ KUMARASWAMY LAYOUT/ KA-BA",
    "NONACC (FI)/ kakscsa08/ RR NAGAR2/ KA-GN",
    "NONACC (FI)/ kakscub08/ BILEKAHALLI3/ KA-SV",
    "NONACC (FI)/ kadopkc07/ HULIMAVU4/ KA-BA",
    "NONACC (FI)/ kaksfcl08/ AKSHAYANAGAR/ KA-GN",
    "NONACC (FI)/ kabacsl08/ BEGUR6/ KA-SV",
    "NONACC (BK)/ kakscsa08/ SINGASANDRA7/ KA-BA",
    "NONACC (FI)/ kacrsfl08/ PARAPPANA AGRAHARA8/ KA-GN",
    "NONACC (FI)/ kabacsl08/ HONGASANDRA/ KA-SV",
    "NONACC (FI)/ kabacsl08/ KAMAKSHIPALYA10/ KA-BA",
    "NONACC (FI)/ kagcsl09/ LAGGERE11/ KA-GN",
    "NONACC (FI)/ kacrsl08/ BYATARAYANAPURA12/ KA-SV",
    "NONACC (BK)/ kadopkc07/ DODDABALLAPUR/ KA-BA",
    "NONACC (FI)/ kacrsfl09/ MADANAYAKANAHALLI14/ KA-GN",
    "NONACC (FI)/ kakscub08/ KUMBALGODU15/ KA-SV",
    "NONACC (FI)/ kacrsl08/ VIRGONAGAR16/ KA-BA",
    "NONACC (FI)/ kakscsa08/ MEDAHALLI/ KA-GN",
    "NONACC (FI)/ kakscsa08/ KR PURAM18/ KA-SV",
    "NONACC (BK)/ kacrsfl08/ SEEGEHALLI19/ KA-BA",
    "NONACC (FI)/ kakscsa08/ AVALAHALLI20/ KA-GN",
    "NONACC (FI)/ kacrsfl08/ GOTTIGERE22/ KA-BA",
    "NONACC (FI)/ kadopkc07/ CHIKKALLASANDRA23/ KA-GN",
    "NONACC (FI)/ kagcsl09/ WHITEFIELD1/ KA-SV",
    "NONACC (FI)/ kacrsfl08/ ELECTRONIC CITY3/ KA-GN",
    "NONACC (FI)/ kadopkc07/ HEBBAL4/ KA-SV",
    "NONACC (FI)/ kadopkc07/ BANASHANKARI5/ KA-BA",
    "NONACC (FI)/ kakscub08/ JP NAGAR7/ KA-SV",
    "NONACC (BK)/ kacrsfl08/ KENGERI8/ KA-BA",
    "NONACC (FI)/ kadopkc07/ MAGADI ROAD9/ KA-GN",
    "NONACC (FI)/ kadopkc07/ PEENYA/ KA-SV",
    "NONACC (FI)/ kakscub08/ NELAMANGALA11/ KA-BA",
    "NONACC (FI)/ kagcsl08/ DEVANAHALLI12/ KA-GN",
    "NONACC (FI)/ kagcsl09/ ATTIBELE13/ KA-SV",
    "NONACC (BK)/ kakscsa08/ BOMMANAHALLI/ KA-BA",
    "NONACC (FI)/ kakscub08/ HENNUR15/ KA-GN",
    "NONACC (FI)/ kagcsl08/ KADUGODI16/ KA-SV",
    "NONACC (FI)/ kakscsa08/ KUNDALAHALLI17/ KA-BA",
    "NONACC (FI)/ kadopkc07/ CV RAMAN NAGAR/ KA-GN",
    "NONACC (FI)/ kadopkc07/ RICHMOND TOWN19/ KA-SV",
    "NONACC (BK)/ kabacsl08/ FRAZER TOWN20/ KA-BA",
    "NONACC (FI)/ kadopkc07/ RT NAGAR21/ KA-GN",
    "NONACC (FI)/ kacrsfl08/ VIDYARANYAPURA/ KA-SV",
    "NONACC (FI)/ kagcsl09/ BANASWADI23/ KA-BA",
    "NONACC (FI)/ kadopkc07/ KASTURINAGAR1/ KA-GN",
    "NONACC (FI)/ kabacsl08/ KALASIPALYA2/ KA-SV",
    "NONACC (BK)/ kagcsl08/ MYSORE ROAD/ KA-BA",
    "NONACC (FI)/ kabacsl08/ CHICKPET4/ KA-GN",
    "NONACC (FI)/ kagcsl09/ ULSOOR5/ KA-SV",
    "NONACC (FI)/ kagcsl08/ SADASHIVANAGAR6/ KA-BA",
    "NONACC (FI)/ kaksfcl08/ SANJAY NAGAR/ KA-GN",
    "NONACC (FI)/ kagcsl09/ JALAHALLI8/ KA-SV",
]

TOTAL_ACC_REFS = len(ACC_REF_LIST)  # 141


def _extract_code_from_acc_ref(acc_ref):
    """Extract second segment from account reference and uppercase it.
    e.g. 'NONACC (FI)/ kaksfcl08/ VARTHUR1/ KA-SV' → 'KAKSFCL08'
    """
    try:
        parts = acc_ref.split('/')
        if len(parts) >= 2:
            return parts[1].strip().upper()
    except Exception:
        pass
    return 'KAKSFCL08'


def _generate_cert_no():
    """Generate: IN-KA + 12 random digits + 1 random capital letter."""
    digits = ''.join(random.choices(string.digits, k=12))
    letter = random.choice(string.ascii_uppercase)
    return f"IN-KA29{digits}{letter}"


def _generate_unique_doc_ref(acc_ref, cert_letter):
    """Generate: SUBIN-KA + code_from_acc_ref + 12 random digits + same letter as cert_no."""
    code = _extract_code_from_acc_ref(acc_ref)
    digits = ''.join(random.choices(string.digits, k=12))
    return f"SUBIN-KA{code}{digits}{cert_letter}"


def _get_shuffled_order():
    """Get or create the shuffled order of account references (stored in DB)."""
    config = EStampConfig.query.filter_by(key='acc_ref_shuffled_order').first()
    if config:
        return json.loads(config.value)

    # First time: create shuffled indices
    indices = list(range(TOTAL_ACC_REFS))
    random.shuffle(indices)

    config = EStampConfig(key='acc_ref_shuffled_order', value=json.dumps(indices))
    db.session.add(config)
    db.session.commit()
    return indices


def _get_current_index():
    """Get the current position in the shuffled order."""
    config = EStampConfig.query.filter_by(key='acc_ref_current_index').first()
    if config:
        return int(config.value)
    # First time
    config = EStampConfig(key='acc_ref_current_index', value='0')
    db.session.add(config)
    db.session.commit()
    return 0


def _advance_index():
    """Move to next account reference. Wraps around to 0 after 141."""
    config = EStampConfig.query.filter_by(key='acc_ref_current_index').first()
    if not config:
        config = EStampConfig(key='acc_ref_current_index', value='0')
        db.session.add(config)

    current = int(config.value)
    next_idx = (current + 1) % TOTAL_ACC_REFS
    config.value = str(next_idx)
    db.session.commit()
    return current  # return the one that was just used


def _get_next_acc_ref():
    """Get the next account reference from shuffled order WITHOUT advancing.
    (Preview only — advancing happens on save.)
    """
    shuffled = _get_shuffled_order()
    current_idx = _get_current_index()
    acc_ref_index = shuffled[current_idx]
    return ACC_REF_LIST[acc_ref_index]


def _consume_next_acc_ref():
    """Get and advance to the next account reference (on save)."""
    shuffled = _get_shuffled_order()
    used_idx = _advance_index()
    acc_ref_index = shuffled[used_idx]
    return ACC_REF_LIST[acc_ref_index]


def _generate_auto_fields():
    """Generate all auto fields for a new certificate preview."""
    acc_ref = _get_next_acc_ref()
    cert_no = _generate_cert_no()
    cert_letter = cert_no[-1]  # last character
    unique_doc_ref = _generate_unique_doc_ref(acc_ref, cert_letter)
    return {
        'certNo': cert_no,
        'accRef': acc_ref,
        'uniqueDocRef': unique_doc_ref,
    }


# ════════════════════════════════════════════════════════
#  API ROUTES
# ════════════════════════════════════════════════════════

@estamp_bp.route('/api/estamp/records', methods=['GET'])
@admin_required
def get_estamp_records():
    """Get all e-Stamp records."""
    try:
        records = EStamp.query.order_by(EStamp.created_at.desc()).all()
        return jsonify({
            'success': True,
            'records': [r.to_dict() for r in records],
            'total': len(records)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@estamp_bp.route('/api/estamp/auto-generate', methods=['GET'])
@admin_required
def auto_generate_fields():
    """Generate auto fields (certNo, accRef, uniqueDocRef) for preview.
    Does NOT consume the account reference — only preview.
    """
    try:
        fields = _generate_auto_fields()
        return jsonify({'success': True, **fields})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@estamp_bp.route('/api/estamp/records', methods=['POST'])
@admin_required
def create_estamp_record():
    """Create a new e-Stamp record. Consumes the account reference on save."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        purchased_by = (data.get('purchasedBy') or '').strip()
        if not purchased_by:
            return jsonify({'success': False, 'message': 'Purchased By is required'}), 400

        # Consume the next account reference (advance the global index)
        saved_acc_ref = _consume_next_acc_ref()

        # Use the cert_no and unique_doc_ref from the form
        # (they were generated during preview via /auto-generate)
        cert_no = data.get('certNo', '')
        cert_letter = cert_no[-1] if cert_no else random.choice(string.ascii_uppercase)

        # Regenerate unique_doc_ref with the SAVED acc_ref to ensure consistency
        unique_doc_ref = _generate_unique_doc_ref(saved_acc_ref, cert_letter)

        record = EStamp(
            created_by=session.get('user_id'),
            cert_no=cert_no,
            cert_date=data.get('certDate', ''),
            acc_ref=saved_acc_ref,
            unique_doc_ref=unique_doc_ref,
            purchased_by=purchased_by,
            doc_desc=data.get('docDesc', ''),
            prop_desc=data.get('propDesc', ''),
            consider_price=data.get('considerPrice', ''),
            first_party=data.get('firstParty', ''),
            second_party=data.get('secondParty', ''),
            stamp_paid_by=data.get('stampPaidBy', ''),
            stamp_duty=data.get('stampDuty', ''),
            amount_words=data.get('amountWords', ''),
            consider_words=data.get('considerWords', ''),
        )

        db.session.add(record)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'e-Stamp certificate saved.',
            'record': record.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@estamp_bp.route('/api/estamp/records/<record_id>', methods=['PUT'])
@admin_required
def update_estamp_record(record_id):
    """Update an existing e-Stamp record. Does NOT consume a new account reference."""
    try:
        record = EStamp.query.get(record_id)
        if not record:
            return jsonify({'success': False, 'message': 'Record not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        purchased_by = (data.get('purchasedBy') or '').strip()
        if not purchased_by:
            return jsonify({'success': False, 'message': 'Purchased By is required'}), 400

        # On update, keep existing certNo/accRef/uniqueDocRef unless explicitly changed
        record.cert_no = data.get('certNo', record.cert_no)
        record.cert_date = data.get('certDate', record.cert_date)
        record.acc_ref = data.get('accRef', record.acc_ref)
        record.unique_doc_ref = data.get('uniqueDocRef', record.unique_doc_ref)
        record.purchased_by = purchased_by
        record.doc_desc = data.get('docDesc', record.doc_desc)
        record.prop_desc = data.get('propDesc', record.prop_desc)
        record.consider_price = data.get('considerPrice', record.consider_price)
        record.first_party = data.get('firstParty', record.first_party)
        record.second_party = data.get('secondParty', record.second_party)
        record.stamp_paid_by = data.get('stampPaidBy', record.stamp_paid_by)
        record.stamp_duty = data.get('stampDuty', record.stamp_duty)
        record.amount_words = data.get('amountWords', record.amount_words)
        record.consider_words = data.get('considerWords', record.consider_words)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Certificate updated.',
            'record': record.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@estamp_bp.route('/api/estamp/records/<record_id>', methods=['DELETE'])
@admin_required
def delete_estamp_record(record_id):
    """Delete an e-Stamp record."""
    try:
        record = EStamp.query.get(record_id)
        if not record:
            return jsonify({'success': False, 'message': 'Record not found'}), 404

        db.session.delete(record)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Record deleted.'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@estamp_bp.route('/api/estamp/stats', methods=['GET'])
@admin_required
def get_estamp_stats():
    """Get e-Stamp usage stats."""
    try:
        total_records = EStamp.query.count()
        current_idx = _get_current_index()
        return jsonify({
            'success': True,
            'totalRecords': total_records,
            'totalAccRefs': TOTAL_ACC_REFS,
            'currentIndex': current_idx,
            'accRefsUsed': current_idx,
            'accRefsRemaining': TOTAL_ACC_REFS - current_idx,
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
