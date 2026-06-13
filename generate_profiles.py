import json
import os
import re
import random
import string
from datetime import date

TODAY = date.today().isoformat()

def make_key(slug):
    prefix = slug[:3].replace('-','')
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{prefix}-{suffix}"

CATEGORIES = {
    "accountants": {
        "plural": "Accountants",
        "singular": "Accountant",
        "page": "/accountants.html",
        "nav_active": "Finance",
        "schema_type": "AccountingService",
    },
    "builders": {
        "plural": "Builders",
        "singular": "Builder",
        "page": "/builders.html",
        "nav_active": "Trades",
        "schema_type": "GeneralContractor",
    },
    "dentists": {
        "plural": "Dentists",
        "singular": "Dentist",
        "page": "/dentists.html",
        "nav_active": "Health",
        "schema_type": "Dentist",
    },
    "electricians": {
        "plural": "Electricians",
        "singular": "Electrician",
        "page": "/electricians.html",
        "nav_active": "Trades",
        "schema_type": "Electrician",
    },
    "gps": {
        "plural": "GPs",
        "singular": "GP",
        "page": "/gps.html",
        "nav_active": "Health",
        "schema_type": "MedicalClinic",
    },
    "lawyers": {
        "plural": "Lawyers",
        "singular": "Lawyer",
        "page": "/lawyers.html",
        "nav_active": "Legal",
        "schema_type": "LegalService",
    },
    "mechanics": {
        "plural": "Mechanics",
        "singular": "Mechanic",
        "page": "/mechanics.html",
        "nav_active": "Trades",
        "schema_type": "AutoRepair",
    },
    "ndis": {
        "plural": "NDIS Providers",
        "singular": "NDIS Provider",
        "page": "/ndis.html",
        "nav_active": "NDIS",
        "schema_type": "LocalBusiness",
    },
    "physiotherapists": {
        "plural": "Physiotherapists",
        "singular": "Physiotherapist",
        "page": "/physiotherapists.html",
        "nav_active": "Health",
        "schema_type": "MedicalBusiness",
    },
    "plumbers": {
        "plural": "Plumbers",
        "singular": "Plumber",
        "page": "/plumbers.html",
        "nav_active": "Trades",
        "schema_type": "Plumber",
    },
    "psychologists": {
        "plural": "Psychologists",
        "singular": "Psychologist",
        "page": "/psychologists.html",
        "nav_active": "Health",
        "schema_type": "MedicalBusiness",
    },
    "removalists": {
        "plural": "Removalists",
        "singular": "Removalist",
        "page": "/removalists.html",
        "nav_active": "Trades",
        "schema_type": "MovingCompany",
    },
}

NEW_BUSINESSES = {
    "accountants": [
        {
            "slug": "garis-group-hamilton",
            "name": "The Garis Group",
            "credentials": "Chartered Accountants & Business Advisors",
            "address": "Level 1/83 Beaumont Street, Hamilton NSW 2303",
            "suburb": "Hamilton",
            "phone": "(02) 4969 4699",
            "website": "https://garisgroup.com.au",
            "services": ["Business Accounting", "Tax Returns", "Business Advisory", "Financial Planning", "BAS & GST", "SMSF"],
            "service_areas": ["Hamilton", "Newcastle", "Hunter Region"],
            "description": "Chartered accountants and business advisors based in Hamilton, serving Newcastle and the Hunter Region with taxation, business advisory, and financial planning services.",
            "hours": "Mon-Fri 8:30am-5:00pm",
            "google_search": "The Garis Group accountant Hamilton NSW",
        },
        {
            "slug": "maxim-accounting-newcastle",
            "name": "Maxim Accounting & Business Advisors",
            "credentials": "Chartered Accountants & Business Advisors",
            "address": "Suite 101/45 Watt Street, Newcastle NSW 2300",
            "suburb": "Newcastle",
            "phone": "(02) 4925 1000",
            "website": "https://maximbas.com.au",
            "services": ["Business Accounting", "Tax Returns", "Business Advisory", "BAS & GST", "Bookkeeping", "SMSF"],
            "service_areas": ["Newcastle", "Hunter Region"],
            "description": "Newcastle-based chartered accountants providing taxation, business advisory, and financial planning services from their Watt Street office.",
            "hours": "Mon-Fri 9:00am-5:00pm",
            "google_search": "Maxim Accounting Business Advisors accountant Newcastle NSW",
        },
        {
            "slug": "kelly-partners-newcastle-west",
            "name": "Kelly+Partners Newcastle",
            "credentials": "Registered Tax Agents & Business Advisors",
            "address": "4 Hall Street, Newcastle West NSW 2302",
            "suburb": "Newcastle West",
            "phone": "1300 802 780",
            "website": "https://kellypartners.com.au",
            "services": ["Business Accounting", "Tax Planning", "Business Advisory", "Wealth Management", "SMSF", "Bookkeeping"],
            "service_areas": ["Newcastle", "Hunter Region"],
            "description": "National accounting firm with a dedicated Newcastle office, providing business advisory, tax planning, and wealth management services to local businesses.",
            "hours": "Mon-Fri 8:30am-5:00pm",
            "google_search": "Kelly Partners Newcastle accountant Newcastle West NSW",
        },
    ],
    "builders": [
        {
            "slug": "arbuilt-newcastle",
            "name": "Arbuilt",
            "credentials": "Licensed Builder",
            "address": "Newcastle NSW 2300",
            "suburb": "Newcastle",
            "phone": "0413 974 487",
            "email": "ryan@arbuilt.com.au",
            "website": "https://arbuilt.com.au",
            "services": ["Residential Renovations", "Extensions", "New Homes", "Knockdown Rebuild", "Custom Builds"],
            "service_areas": ["Newcastle", "Hunter Region", "Lake Macquarie"],
            "description": "Newcastle-based building company specialising in residential renovations, extensions, and new home constructions across the Hunter Region.",
            "hours": "Mon-Fri 7:00am-5:00pm",
            "google_search": "Arbuilt builder Newcastle NSW",
        },
        {
            "slug": "jlc-building-wallsend",
            "name": "JLC Building Developments",
            "credentials": "Licensed Builder",
            "address": "Wallsend NSW 2287",
            "suburb": "Wallsend",
            "phone": "1300 878 929",
            "website": "https://jlcbuildingdevelopments.com.au",
            "services": ["Residential Construction", "Commercial Construction", "Renovations", "New Homes", "Developments"],
            "service_areas": ["Wallsend", "Newcastle", "Hunter Region"],
            "description": "Wallsend-based builder delivering quality residential and commercial construction projects across Newcastle and the Hunter Region.",
            "hours": "Mon-Fri 7:00am-5:00pm",
            "google_search": "JLC Building Developments builder Wallsend NSW",
        },
        {
            "slug": "upton-construction-rutherford",
            "name": "Upton Construction",
            "credentials": "Licensed Builder",
            "address": "Rutherford NSW 2320",
            "suburb": "Rutherford",
            "email": "admin@uptonconstruction.com.au",
            "website": "https://uptonconstruction.com.au",
            "services": ["Residential Construction", "Commercial Construction", "Renovations", "Custom Builds", "Project Management"],
            "service_areas": ["Rutherford", "Maitland", "Newcastle", "Hunter Valley"],
            "description": "Rutherford-based construction company offering residential and commercial building services throughout the Hunter Valley and Newcastle region.",
            "hours": "Mon-Fri 7:00am-5:00pm",
            "google_search": "Upton Construction builder Rutherford NSW",
        },
    ],
    "dentists": [
        {
            "slug": "dentist-for-chickens-swansea",
            "name": "Dentist for Chickens",
            "credentials": "General & Family Dentist",
            "address": "Shop 2/204-206 Pacific Highway, Swansea NSW 2281",
            "suburb": "Swansea",
            "phone": "(02) 4971 0144",
            "website": "https://dentistforchickens.com.au",
            "services": ["General Dentistry", "Cosmetic Dentistry", "Emergency Dental", "Family Dentistry", "Teeth Whitening", "Dental Checkups"],
            "service_areas": ["Swansea", "Lake Macquarie", "Newcastle"],
            "description": "Friendly family dental practice in Swansea serving the Lake Macquarie community with general, cosmetic, and emergency dental care.",
            "hours": "Mon-Fri 8:30am-5:00pm",
            "google_search": "Dentist for Chickens Swansea Dental Care dentist Swansea NSW",
        },
        {
            "slug": "merewether-dental-merewether",
            "name": "Merewether Dental Clinic",
            "credentials": "General & Cosmetic Dentist",
            "address": "31 Llewellyn Street, Merewether NSW 2291",
            "suburb": "Merewether",
            "phone": "(02) 4963 5009",
            "website": "https://merewetherdental.com.au",
            "services": ["General Dentistry", "Cosmetic Dentistry", "Family Dentistry", "Dental Implants", "Orthodontics", "Teeth Whitening"],
            "service_areas": ["Merewether", "Newcastle", "Hunter Region"],
            "description": "Established dental practice in Merewether providing comprehensive general and cosmetic dental care to patients across Newcastle's inner suburbs.",
            "hours": "Mon-Fri 8:30am-5:30pm",
            "google_search": "Merewether Dental Clinic dentist Merewether NSW",
        },
        {
            "slug": "evolution-dental-care-hamilton",
            "name": "Evolution Dental Care",
            "credentials": "General & Cosmetic Dentist",
            "address": "20 Beaumont Street, Hamilton NSW 2303",
            "suburb": "Hamilton",
            "phone": "(02) 4040 0560",
            "email": "reception@evolutiondentalcare.com.au",
            "website": "https://evolutiondentalcare.com.au",
            "services": ["General Dentistry", "Cosmetic Dentistry", "Orthodontics", "Teeth Whitening", "AIRFLOW Dental Spa", "Children's Dentistry"],
            "service_areas": ["Hamilton", "Newcastle", "Hunter Region"],
            "description": "Modern dental practice on Hamilton's Beaumont Street offering a full range of dental services including cosmetic dentistry, orthodontics, and AIRFLOW dental treatments.",
            "hours": "Mon-Thu 7:00am-6:00pm, Fri 9:00am-4:00pm",
            "google_search": "Evolution Dental Care dentist Hamilton NSW",
        },
    ],
    "electricians": [
        {
            "slug": "your-favourite-electrician-newcastle",
            "name": "Your Favourite Electrician",
            "credentials": "Licensed Electrician",
            "address": "Newcastle NSW 2300",
            "suburb": "Newcastle",
            "phone": "0418 461 946",
            "website": "https://yourfavouriteelectrician.com.au",
            "services": ["Residential Electrical", "Commercial Electrical", "Switchboard Upgrades", "Safety Inspections", "LED Lighting", "Power Points"],
            "service_areas": ["Newcastle", "Hunter Region", "Lake Macquarie"],
            "description": "Reliable local electrician servicing Newcastle and the Hunter Region for all residential and commercial electrical needs.",
            "hours": "Mon-Fri 7:00am-5:00pm",
            "google_search": "Your Favourite Electrician electrician Newcastle NSW",
        },
        {
            "slug": "weiley-electrical-mayfield-west",
            "name": "Weiley Electrical",
            "credentials": "Licensed Electrical Contractors",
            "address": "Unit 7/11 McIntosh Drive, Mayfield West NSW 2304",
            "suburb": "Mayfield West",
            "phone": "(02) 6884 9292",
            "website": "https://weiley.com.au",
            "services": ["Commercial Electrical", "Industrial Electrical", "Residential Electrical", "Data Cabling", "Switchboards", "Testing & Tagging"],
            "service_areas": ["Mayfield West", "Newcastle", "Hunter Region"],
            "description": "Mayfield West-based electrical contractors delivering quality residential and commercial electrical services across Newcastle and the Hunter Region.",
            "hours": "Mon-Fri 7:00am-5:00pm",
            "google_search": "Weiley Electrical electrician Mayfield West NSW",
        },
        {
            "slug": "darren-worpel-electrical-charlestown",
            "name": "Darren Worpel Electrical",
            "credentials": "Licensed Electrician",
            "address": "Charlestown NSW 2290",
            "suburb": "Charlestown",
            "phone": "0407 000 329",
            "website": "https://darrenworpelelectrical.com.au",
            "services": ["Residential Electrical", "Commercial Electrical", "Fault Finding", "Switchboard Upgrades", "Renovation Wiring", "Safety Switches"],
            "service_areas": ["Charlestown", "Newcastle", "Lake Macquarie"],
            "description": "Charlestown-based licensed electrician providing quality electrical services for residential and commercial customers across the Newcastle region.",
            "hours": "Mon-Fri 7:00am-5:00pm",
            "google_search": "Darren Worpel Electrical electrician Charlestown NSW",
        },
    ],
    "gps": [
        {
            "slug": "wallsend-gp-clinic",
            "name": "Wallsend GP Clinic",
            "credentials": "General Practice",
            "address": "Suite 5/136 Nelson Street, Wallsend NSW 2287",
            "suburb": "Wallsend",
            "phone": "(02) 4950 2338",
            "website": "https://wallsendgp.com.au",
            "services": ["General Practice", "Bulk Billing", "Preventive Health", "Chronic Disease Management", "Mental Health Care Plans", "Vaccinations"],
            "service_areas": ["Wallsend", "Newcastle", "Hunter Region"],
            "description": "Bulk-billing general practice clinic in Wallsend providing comprehensive primary healthcare services to the local community.",
            "hours": "Mon-Fri 8:00am-5:30pm",
            "google_search": "Wallsend GP Clinic general practitioner Wallsend NSW",
        },
        {
            "slug": "hello-health-family-practice-wallsend",
            "name": "Hello Health Family Practice",
            "credentials": "General Practice",
            "address": "30 Newcastle Road, Wallsend NSW 2287",
            "suburb": "Wallsend",
            "phone": "(02) 4951 3988",
            "website": "https://hellohealthfp.com.au",
            "services": ["General Practice", "Family Medicine", "Women's Health", "Children's Health", "Chronic Disease Management", "Mental Health"],
            "service_areas": ["Wallsend", "Newcastle", "Hunter Region"],
            "description": "Modern family medical practice in Wallsend focused on providing accessible, patient-centred care to individuals and families.",
            "hours": "Mon-Fri 8:00am-5:30pm",
            "google_search": "Hello Health Family Practice GP Wallsend NSW",
        },
        {
            "slug": "wallsend-family-medical-centre",
            "name": "Wallsend Family Medical Centre",
            "credentials": "General Practice",
            "address": "124 Nelson Street, Wallsend NSW 2287",
            "suburb": "Wallsend",
            "phone": "(02) 4955 8341",
            "website": "https://wallsendmedical.com.au",
            "services": ["General Practice", "Family Medicine", "Preventive Health", "Chronic Disease Management", "Mental Health", "Vaccinations"],
            "service_areas": ["Wallsend", "Newcastle", "Hunter Region"],
            "description": "Established family medical centre in Wallsend providing comprehensive general practice services to the local community.",
            "hours": "Mon-Fri 8:00am-5:30pm",
            "google_search": "Wallsend Family Medical Centre GP Wallsend NSW",
        },
    ],
    "lawyers": [
        {
            "slug": "gillard-family-lawyers-newcastle",
            "name": "Gillard Family Lawyers",
            "credentials": "Family Law Specialists",
            "address": "Unit 24/1 Honeysuckle Drive, Newcastle NSW 2300",
            "suburb": "Newcastle",
            "phone": "(02) 4910 0740",
            "website": "https://gillardfamilylawyers.com.au",
            "services": ["Family Law", "Divorce", "Property Settlements", "Parenting Matters", "Domestic Violence Orders", "Child Support"],
            "service_areas": ["Newcastle", "Hunter Region", "Central Coast"],
            "description": "Newcastle-based family law firm specialising in divorce, property settlements, parenting matters, and domestic violence proceedings.",
            "hours": "Mon-Fri 9:00am-5:00pm",
            "google_search": "Gillard Family Lawyers lawyer Newcastle NSW",
        },
        {
            "slug": "east-coast-law-broadmeadow",
            "name": "East Coast Law Group",
            "credentials": "Solicitors & Barristers",
            "address": "Level 1/5 Brunker Road, Broadmeadow NSW 2292",
            "suburb": "Broadmeadow",
            "phone": "(02) 4920 6511",
            "website": "https://eastcoastlaw.com.au",
            "services": ["Commercial Law", "Property Law", "Employment Law", "Dispute Resolution", "Conveyancing", "Contract Law"],
            "service_areas": ["Broadmeadow", "Newcastle", "Hunter Region"],
            "description": "Broadmeadow law firm providing comprehensive legal services across commercial law, property, employment, and dispute resolution.",
            "hours": "Mon-Fri 9:00am-5:00pm",
            "google_search": "East Coast Law Group lawyer Broadmeadow NSW",
        },
        {
            "slug": "cdg-law-newcastle",
            "name": "CDG Law",
            "credentials": "Solicitors",
            "address": "Unit 7/1 Honeysuckle Drive, Newcastle NSW 2300",
            "suburb": "Newcastle",
            "phone": "(02) 6572 2911",
            "website": "https://cdglaw.com.au",
            "services": ["Family Law", "Commercial Law", "Conveyancing", "Wills & Estates", "Property Law", "Dispute Resolution"],
            "service_areas": ["Newcastle", "Hunter Region", "Maitland"],
            "description": "Newcastle CBD law firm offering a wide range of legal services including family law, commercial matters, conveyancing, and wills and estates.",
            "hours": "Mon-Fri 9:00am-5:00pm",
            "google_search": "CDG Law solicitor Newcastle NSW",
        },
    ],
    "mechanics": [
        {
            "slug": "newy-mobile-mechanics-belmont-north",
            "name": "Newy Mobile Mechanics",
            "credentials": "Mobile Mechanic",
            "address": "Belmont North NSW 2280",
            "suburb": "Belmont North",
            "phone": "0410 188 333",
            "website": "https://newymobilemechanics.com.au",
            "services": ["Mobile Mechanic", "Log Book Servicing", "Brake Repairs", "Roadside Assistance", "Pre-Purchase Inspections", "Tyres"],
            "service_areas": ["Belmont North", "Lake Macquarie", "Newcastle"],
            "description": "Mobile mechanic service based in Belmont North, bringing professional car servicing and repairs directly to your home or workplace.",
            "hours": "Mon-Sat 7:00am-5:00pm",
            "google_search": "Newy Mobile Mechanics mechanic Belmont North NSW",
        },
        {
            "slug": "ingear-mechanical-tomago",
            "name": "InGear Mechanical",
            "credentials": "Qualified Automotive Technicians",
            "address": "2/13 Kennington Drive, Tomago NSW 2322",
            "suburb": "Tomago",
            "phone": "(02) 4964 9965",
            "website": "https://ingearmechanical.com.au",
            "services": ["Log Book Servicing", "Mechanical Repairs", "4WD Servicing", "Brake & Clutch", "Suspension", "Diagnostics"],
            "service_areas": ["Tomago", "Newcastle", "Hunter Region"],
            "description": "Tomago-based automotive workshop servicing passenger vehicles and 4WDs with log book servicing, mechanical repairs, and performance upgrades.",
            "hours": "Mon-Fri 7:30am-5:00pm",
            "google_search": "InGear Mechanical mechanic Tomago NSW",
        },
        {
            "slug": "cherrys-automotive-maitland",
            "name": "Cherry's Automotive Repairs",
            "credentials": "Qualified Mechanics",
            "address": "89 Elgin Street, Maitland NSW 2320",
            "suburb": "Maitland",
            "phone": "(02) 4934 7262",
            "website": "https://cherrysautomotive.com.au",
            "services": ["Mechanical Repairs", "Log Book Servicing", "Brake Repairs", "Engine Diagnostics", "Air Conditioning", "Tyres"],
            "service_areas": ["Maitland", "Hunter Region", "Newcastle"],
            "description": "Family-owned automotive repair workshop in Maitland with decades of experience servicing cars, vans, and light commercial vehicles.",
            "hours": "Mon-Fri 8:00am-5:00pm",
            "google_search": "Cherry's Automotive Repairs mechanic Maitland NSW",
        },
    ],
    "ndis": [
        {
            "slug": "empowered-community-services-cardiff",
            "name": "Empowered Community Services",
            "credentials": "Registered NDIS Provider",
            "address": "Suite 101/286 Main Road, Cardiff NSW 2285",
            "suburb": "Cardiff",
            "phone": "(02) 4054 9286",
            "website": "https://empoweredcommunityservices.com",
            "services": ["Support Coordination", "Community Access", "Daily Living Assistance", "Personal Care", "NDIS Plan Management", "Social Support"],
            "service_areas": ["Cardiff", "Newcastle", "Hunter Region", "Lake Macquarie"],
            "description": "NDIS-registered provider in Cardiff offering support coordination, community access, and daily living assistance to people with disability across the Hunter Region.",
            "hours": "Mon-Fri 9:00am-5:00pm",
            "google_search": "Empowered Community Services NDIS provider Cardiff NSW",
        },
        {
            "slug": "create-disability-services-newcastle",
            "name": "Create Disability Services",
            "credentials": "Registered NDIS Provider",
            "address": "Newcastle NSW 2300",
            "suburb": "Newcastle",
            "phone": "(02) 4930 0957",
            "website": "https://createdisabilityservices.com.au",
            "services": ["Daily Living Support", "Community Participation", "Supported Independent Living", "Capacity Building", "Respite Care", "Personal Care"],
            "service_areas": ["Newcastle", "Hunter Region", "Lake Macquarie"],
            "description": "Newcastle-based NDIS provider delivering personalised disability support services including daily living assistance, community participation, and supported independent living.",
            "hours": "Mon-Fri 9:00am-5:00pm",
            "google_search": "Create Disability Services NDIS provider Newcastle NSW",
        },
        {
            "slug": "paramount-care-solutions-glendale",
            "name": "Paramount Care Solutions",
            "credentials": "Registered NDIS Provider",
            "address": "Unit 3/545 Main Road, Glendale NSW 2285",
            "suburb": "Glendale",
            "phone": "(02) 4044 3787",
            "website": "https://paramountcaresolutions.com.au",
            "services": ["Support Coordination", "Mental Health Support", "In-Home Care", "Community Access", "NDIS Plan Management", "Aged Care"],
            "service_areas": ["Glendale", "Newcastle", "Hunter Region", "Lake Macquarie"],
            "description": "Glendale-based NDIS and aged care provider offering support coordination, mental health support, and in-home care services across the Hunter Region.",
            "hours": "Mon-Fri 9:00am-5:00pm",
            "google_search": "Paramount Care Solutions NDIS provider Glendale NSW",
        },
    ],
    "physiotherapists": [
        {
            "slug": "charlestown-physiotherapy-gateshead",
            "name": "Charlestown Physiotherapy",
            "credentials": "Registered Physiotherapists",
            "address": "1 Skyline Way, Gateshead NSW 2290",
            "suburb": "Gateshead",
            "phone": "(02) 4942 1322",
            "website": "https://charlestownphysio.com.au",
            "services": ["Sports Physiotherapy", "Musculoskeletal Therapy", "Post-Surgical Rehab", "Dry Needling", "Exercise Physiology", "Hydrotherapy"],
            "service_areas": ["Gateshead", "Charlestown", "Newcastle", "Lake Macquarie"],
            "description": "Established physiotherapy clinic in Gateshead providing evidence-based treatment for sports injuries, musculoskeletal conditions, and post-surgical rehabilitation.",
            "hours": "Mon-Fri 8:00am-6:00pm",
            "google_search": "Charlestown Physiotherapy physiotherapist Gateshead NSW",
        },
        {
            "slug": "transcend-health-broadmeadow",
            "name": "Transcend Health",
            "credentials": "Allied Health Professionals",
            "address": "Level 1/58 Broadmeadow Road, Broadmeadow NSW 2292",
            "suburb": "Broadmeadow",
            "phone": "(02) 4961 3399",
            "website": "https://transcendhealth.com.au",
            "services": ["Physiotherapy", "Exercise Physiology", "Occupational Therapy", "NDIS Support", "Workers Compensation", "Rehabilitation"],
            "service_areas": ["Broadmeadow", "Newcastle", "Hunter Region"],
            "description": "Broadmeadow-based allied health clinic providing physiotherapy, exercise physiology, and occupational therapy services to clients across the Hunter Region.",
            "hours": "Mon-Fri 8:00am-6:00pm",
            "google_search": "Transcend Health physiotherapist Broadmeadow NSW",
        },
        {
            "slug": "back-in-motion-cessnock",
            "name": "Back In Motion Cessnock",
            "credentials": "Registered Physiotherapists",
            "address": "298 Maitland Road, Cessnock NSW 2325",
            "suburb": "Cessnock",
            "phone": "(02) 4990 4540",
            "website": "https://backinmotion.com.au/clinics/cessnock",
            "services": ["Physiotherapy", "Sports Injury Treatment", "Clinical Pilates", "Dry Needling", "Workplace Rehab", "NDIS"],
            "service_areas": ["Cessnock", "Hunter Valley", "Newcastle"],
            "description": "Physiotherapy and allied health clinic in Cessnock, part of the Back In Motion national network, delivering evidence-based care and personalised treatment programs.",
            "hours": "Mon-Fri 8:00am-5:30pm",
            "google_search": "Back In Motion Cessnock physiotherapist Cessnock NSW",
        },
    ],
    "plumbers": [
        {
            "slug": "dsr-plumbing-ashtonfield",
            "name": "DSR Plumbing",
            "credentials": "Licensed Plumber & Gas Fitter",
            "address": "25 Galway Bay Drive, Ashtonfield NSW 2323",
            "suburb": "Ashtonfield",
            "phone": "0407 723 634",
            "website": "https://dsrplumbing.com.au",
            "services": ["Residential Plumbing", "Commercial Plumbing", "Hot Water Systems", "Drainage", "Gas Fitting", "Blocked Drains"],
            "service_areas": ["Ashtonfield", "Maitland", "Newcastle", "Hunter Region"],
            "description": "Ashtonfield-based licensed plumber serving the Hunter Region with residential and commercial plumbing, drainage, hot water systems, and gas fitting.",
            "hours": "Mon-Fri 7:00am-5:00pm",
            "google_search": "DSR Plumbing plumber Ashtonfield NSW",
        },
        {
            "slug": "pro-plumb-newcastle",
            "name": "Pro Plumb Newcastle",
            "credentials": "Licensed Plumber",
            "address": "18 Wolfe Street, Newcastle NSW 2300",
            "suburb": "Newcastle",
            "phone": "0400 080 563",
            "website": "https://proplumbnewcastle.com",
            "services": ["Residential Plumbing", "Commercial Plumbing", "Blocked Drains", "Hot Water Systems", "Gas Fitting", "Renovation Plumbing"],
            "service_areas": ["Newcastle", "Hunter Region", "Central Coast"],
            "description": "Newcastle CBD-based plumbing business offering professional residential and commercial plumbing services across Newcastle, the Hunter and Central Coast.",
            "hours": "Mon-Fri 7:00am-5:00pm",
            "google_search": "Pro Plumb Newcastle plumber Newcastle NSW",
        },
        {
            "slug": "cdl-plumbing-rankin-park",
            "name": "CDL Plumbing Drainage Gas",
            "credentials": "Licensed Plumber & Gas Fitter",
            "address": "12 Dean Parade, Rankin Park NSW 2287",
            "suburb": "Rankin Park",
            "phone": "0499 192 821",
            "email": "admin@cdlplumbing.net",
            "website": "https://cdlplumbdraingas.com.au",
            "services": ["Residential Plumbing", "Drainage", "Gas Fitting", "Blocked Drains", "Hot Water Systems", "Emergency Plumbing"],
            "service_areas": ["Rankin Park", "Newcastle", "Lake Macquarie"],
            "description": "Family-owned Rankin Park plumbing business with over 15 years experience providing plumbing, drainage, and gas fitting services to Newcastle and Lake Macquarie.",
            "hours": "Mon-Fri 7:00am-5:00pm",
            "google_search": "CDL Plumbing Drainage Gas plumber Rankin Park NSW",
        },
    ],
    "psychologists": [
        {
            "slug": "thrive-psychology-newcastle-west",
            "name": "Thrive Psychology Newcastle",
            "credentials": "Registered Psychologists",
            "address": "Unit 9/710 Hunter Street, Newcastle West NSW 2302",
            "suburb": "Newcastle West",
            "phone": "(02) 4942 0700",
            "website": "https://thrivepsychology.com.au",
            "services": ["Individual Therapy", "Couples Counselling", "Anxiety Treatment", "Depression Treatment", "Psychological Assessment", "Trauma Therapy"],
            "service_areas": ["Newcastle West", "Newcastle", "Hunter Region"],
            "description": "Newcastle West psychology practice providing individual therapy, couples counselling, and psychological assessments for adults and young people.",
            "hours": "Mon-Fri 9:00am-5:30pm",
            "google_search": "Thrive Psychology Newcastle psychologist Newcastle West NSW",
        },
        {
            "slug": "mvb-psychology-newcastle",
            "name": "MVB Psychology & Consultancy Services",
            "credentials": "Registered Psychologist",
            "address": "107/17 Bolton Street, Newcastle NSW 2300",
            "suburb": "Newcastle",
            "phone": "(02) 4910 4005",
            "website": "https://mvbpsychology.com.au",
            "services": ["Psychological Assessment", "Individual Therapy", "NDIS Psychology", "Cognitive Assessments", "Mental Health Treatment", "Consultancy"],
            "service_areas": ["Newcastle", "Hunter Region"],
            "description": "Newcastle City psychology practice providing a broad range of psychological services including assessments, individual therapy, and NDIS-funded supports.",
            "hours": "Mon-Fri 9:00am-5:00pm",
            "google_search": "MVB Psychology Consultancy psychologist Newcastle NSW",
        },
        {
            "slug": "newcastle-neuropsych",
            "name": "Newcastle NeuroHealth",
            "credentials": "Clinical Neuropsychologist",
            "address": "17 Bolton Street, Newcastle NSW 2300",
            "suburb": "Newcastle",
            "phone": "(02) 4910 4043",
            "website": "https://newcastleneuropsych.com.au",
            "services": ["Neuropsychological Assessment", "Brain Injury Evaluation", "Dementia Assessment", "ADHD Assessment", "Cognitive Assessment", "Expert Reports"],
            "service_areas": ["Newcastle", "Hunter Region", "Central Coast"],
            "description": "Clinical neuropsychology practice in Newcastle CBD providing specialised neuropsychological assessments for adults with brain injury, dementia, and neurodevelopmental conditions.",
            "hours": "Mon-Fri 9:00am-5:00pm",
            "google_search": "Newcastle NeuroHealth neuropsychologist Newcastle NSW",
        },
    ],
    "removalists": [
        {
            "slug": "novocastrian-removals-newcastle",
            "name": "Novocastrian Removals",
            "credentials": "Professional Removalists",
            "address": "Newcastle NSW 2300",
            "suburb": "Newcastle",
            "phone": "1300 166 838",
            "website": "https://novocastrianremovals.com.au",
            "services": ["Local Removals", "Interstate Removals", "Office Removals", "Packing Services", "Storage Solutions", "Furniture Assembly"],
            "service_areas": ["Newcastle", "Hunter Region", "Interstate"],
            "description": "Local Newcastle removalist company providing professional, careful removals for homes and offices across Newcastle, Hunter Region, and interstate.",
            "hours": "Mon-Sat 7:00am-6:00pm",
            "google_search": "Novocastrian Removals removalist Newcastle NSW",
        },
        {
            "slug": "remarkable-removals-newcastle",
            "name": "Remarkable Removals",
            "credentials": "Professional Removalists",
            "address": "Newcastle NSW 2300",
            "suburb": "Newcastle",
            "phone": "0416 423 211",
            "website": "https://remarkableremovals.com.au",
            "services": ["House Removals", "Office Removals", "Furniture Removals", "Packing Services", "Local Moves", "Interstate"],
            "service_areas": ["Newcastle", "Hunter Region", "Lake Macquarie"],
            "description": "Newcastle-based removalist service committed to careful and efficient home and office moves across the Hunter Region and beyond.",
            "hours": "Mon-Sat 7:00am-6:00pm",
            "google_search": "Remarkable Removals removalist Newcastle NSW",
        },
        {
            "slug": "gentle-giant-removals-newcastle",
            "name": "Gentle Giant Removals",
            "credentials": "Professional Removalists",
            "address": "Newcastle NSW 2300",
            "suburb": "Newcastle",
            "phone": "0404 958 455",
            "website": "https://gentlegiantremovals.com.au",
            "services": ["Local Removals", "Interstate Removals", "Office Removals", "Storage", "Piano Removals", "Packing"],
            "service_areas": ["Newcastle", "Central Coast", "Hunter Region", "Interstate"],
            "description": "Experienced Newcastle and Central Coast removalist with over 40 years in the industry, known for careful, reliable relocations for homes and businesses.",
            "hours": "Mon-Sat 7:00am-6:00pm",
            "google_search": "Gentle Giant Removals removalist Newcastle NSW",
        },
    ],
}


def get_nav_html(active):
    items = [
        ("Health", "/gps.html"),
        ("Trades", "/plumbers.html"),
        ("Legal", "/lawyers.html"),
        ("Finance", "/accountants.html"),
        ("NDIS", "/ndis.html"),
    ]
    li_items = []
    for label, href in items:
        if label == active:
            li_items.append(f'<li><a href="{href}" style="color:#fff">{label}</a></li>')
        else:
            li_items.append(f'<li><a href="{href}">{label}</a></li>')
    return '\n      '.join(li_items)


def generate_html(cat, b, secret_key):
    cat_info = CATEGORIES[cat]
    plural = cat_info["plural"]
    singular = cat_info["singular"]
    page = cat_info["page"]
    nav_active = cat_info["nav_active"]
    schema_type = cat_info.get("schema_type", "LocalBusiness")
    
    slug = b["slug"]
    name = b["name"]
    address = b["address"]
    suburb = b["suburb"]
    phone = b.get("phone", "")
    email = b.get("email", "")
    website = b.get("website", "")
    services = b.get("services", [])
    service_areas = b.get("service_areas", [])
    description = b.get("description", "")
    credentials = b.get("credentials", "")
    hours = b.get("hours", "Mon-Fri 9:00am-5:00pm")
    google_search = b.get("google_search", f"{name} {singular} Newcastle NSW")
    
    # Derive website display name
    website_display = website.replace("https://", "").replace("http://", "").rstrip("/")
    
    tags_html = "".join(f'<span class="tag">{s}</span>' for s in services[:6])
    services_html = "".join(f'<span class="tag" style="font-size:13px;padding:5px 12px;">{s}</span>' for s in services)
    areas_html = "".join(f'<span class="ref-chip">{a}</span>' for a in service_areas)
    
    phone_detail = f'<div class="detail-row"><span class="detail-icon">&#128222;</span><a href="tel:{phone}" style="color:var(--ink);text-decoration:none;">{phone}</a></div>' if phone else ""
    email_detail = f'<div class="detail-row"><span class="detail-icon">&#9993;</span><a href="mailto:{email}" style="color:var(--accent);text-decoration:none;">{email}</a></div>' if email else ""
    website_detail = f'<div class="detail-row"><span class="detail-icon">&#127758;</span><a href="{website}" target="_blank" rel="noopener" style="color:var(--accent);text-decoration:none;">{website_display}</a></div>' if website else ""
    
    call_btn = f'<a href="tel:{phone}" class="btn-secondary">Call Now</a>' if phone else ""
    visit_btn = f'<a href="{website}" target="_blank" rel="noopener" class="btn-primary">Visit Website</a>' if website else ""
    
    nav_html = get_nav_html(nav_active)
    
    # Schema address parts
    street = address.split(",")[0] if "," in address else address
    
    schema_obj = {
        "@type": schema_type,
        "name": name,
        "url": f"https://newcastlelocal.com.au/profiles/{cat}/{slug}.html",
        "description": description,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": street,
            "addressLocality": suburb,
            "addressRegion": "NSW",
            "addressCountry": "AU"
        },
        "areaServed": {
            "@type": "City",
            "name": "Newcastle",
            "addressRegion": "NSW"
        }
    }
    if phone:
        schema_obj["telephone"] = phone
    if website:
        schema_obj["sameAs"] = website
    
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            schema_obj,
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://newcastlelocal.com.au"},
                    {"@type": "ListItem", "position": 2, "name": plural, "item": f"https://newcastlelocal.com.au{page}"},
                    {"@type": "ListItem", "position": 3, "name": name, "item": f"https://newcastlelocal.com.au/profiles/{cat}/{slug}.html"},
                ]
            }
        ]
    }
    schema_json = json.dumps(schema, indent=2)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — Newcastle {singular} | NewcastleLocal</title>
<meta name="description" content="{description}">
<link rel="stylesheet" href="/css/style.css">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap" rel="stylesheet">
<style>
  .profile-hero{{background:var(--ink);padding:56px 24px 64px;position:relative;overflow:hidden;}}
  .profile-hero::before{{content:'';position:absolute;top:-60px;right:-60px;width:360px;height:360px;border-radius:50%;background:radial-gradient(circle,rgba(45,95,78,0.15) 0%,transparent 70%);}}
  .profile-hero-inner{{max-width:1100px;margin:0 auto;}}
  .profile-back{{color:#888;font-size:13px;text-decoration:none;display:inline-flex;align-items:center;gap:6px;margin-bottom:24px;transition:color 0.15s;}}
  .profile-back:hover{{color:#fff;}}
  .profile-name{{font-family:'Playfair Display',serif;font-size:clamp(28px,4vw,46px);color:#fff;line-height:1.1;margin-bottom:8px;}}
  .profile-credentials{{color:#aaa;font-size:14px;margin-bottom:20px;}}
  .profile-tags{{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:20px;}}
  .profile-status{{display:inline-flex;align-items:center;gap:8px;padding:8px 18px;border-radius:3px;font-size:13px;font-weight:600;}}
  .profile-body{{max-width:1100px;margin:0 auto;padding:48px 24px;display:grid;grid-template-columns:1fr 300px;gap:48px;align-items:start;}}
  .profile-section{{margin-bottom:36px;}}
  .profile-section h2{{font-family:'Playfair Display',serif;font-size:22px;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid var(--rule);}}
  .profile-section p{{font-size:15px;color:#444;line-height:1.8;margin-bottom:12px;}}
  .detail-card{{background:var(--warm-white);border:1px solid var(--rule);border-radius:4px;padding:24px;position:sticky;top:80px;}}
  .detail-card h3{{font-size:11px;font-weight:500;letter-spacing:0.1em;text-transform:uppercase;color:var(--muted);margin-bottom:18px;}}
  .detail-row{{display:flex;align-items:flex-start;gap:10px;font-size:14px;color:var(--ink);margin-bottom:14px;line-height:1.5;}}
  .detail-icon{{font-size:16px;flex-shrink:0;margin-top:1px;}}
  .detail-divider{{border:none;border-top:1px solid var(--rule);margin:18px 0;}}
  .referral-list{{display:flex;flex-wrap:wrap;gap:5px;}}
  .ref-chip{{padding:3px 10px;background:var(--cream);border-radius:2px;font-size:12px;color:var(--muted);}}
  .btn-group{{display:flex;flex-direction:column;gap:8px;margin-top:18px;}}
  .update-link{{display:block;text-align:center;font-size:11px;color:var(--muted);text-decoration:none;margin-top:14px;padding-top:14px;border-top:1px solid var(--rule);}}
  .update-link:hover{{color:var(--accent);}}
  .delete-link{{display:block;text-align:center;font-size:11px;color:#c62828;text-decoration:none;margin-top:8px;}}
  .delete-link:hover{{text-decoration:underline;}}
  @media(max-width:768px){{.profile-body{{grid-template-columns:1fr;}}.detail-card{{position:static;}}}}
</style>
<!-- SEO-INJECT-START -->
<link rel="canonical" href="https://newcastlelocal.com.au/profiles/{cat}/{slug}.html">
<meta name="robots" content="index, follow">
<meta property="og:title" content="{name} — Newcastle {singular} | NewcastleLocal">
<meta property="og:description" content="{description}">
<meta property="og:url" content="https://newcastlelocal.com.au/profiles/{cat}/{slug}.html">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Newcastle Local">
<meta property="og:image" content="https://newcastlelocal.com.au/css/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{name} — Newcastle {singular} | NewcastleLocal">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="https://newcastlelocal.com.au/css/og-image.png">
<script type="application/ld+json">
{schema_json}
</script>
<!-- SEO-INJECT-END -->
</head>
<body>
<header class="site-header">
  <div class="site-header-inner">
    <a href="/index.html" class="site-logo">Newcastle<span>Local</span></a>
    <nav><ul class="site-nav">
      {nav_html}
      <li><a href="/list.html" style="color:var(--gold)">List Your Business</a></li>
    </ul></nav>
  </div>
</header>
<div class="breadcrumb-bar">
  <div class="breadcrumb-inner">
    <a href="/index.html">Home</a><span>/</span>
    <a href="{page}">{plural}</a><span>/</span>
    {name}
  </div>
</div>
<section class="profile-hero">
  <div class="profile-hero-inner">
    <a href="{page}" class="profile-back">&larr; Back to all {plural.lower()}</a>
    <div class="profile-name">{name}</div>
    <div class="profile-credentials">{credentials}</div>
    <div class="profile-tags">{tags_html}</div>
    <div class="profile-status" id="statusBadge" style="background:#e8f5e9;color:#2e7d32;">&#x2713; Active listing</div>
  </div>
</section>
<div class="profile-body" data-slug="{slug}" data-key="{secret_key}">
  <div>
    <div class="profile-section">
      <h2>About {name}</h2>
      <p>{description}</p>
    </div>
    <div class="profile-section">
      <h2>Services</h2>
      <div style="display:flex;flex-wrap:wrap;gap:8px;">
        {services_html}
      </div>
    </div>
    <div class="profile-section">
      <h2>Service Areas</h2>
      <div class="referral-list">{areas_html}</div>
    </div>
  </div>
  <aside>
    <div class="detail-card">
      <h3>Contact &amp; Details</h3>
      <div class="detail-row"><span class="detail-icon">&#128205;</span>{address}</div>
      {phone_detail}
      {email_detail}
      {website_detail}
      <div class="detail-row"><span class="detail-icon">&#128336;</span>{hours}</div>
      <hr class="detail-divider">
      <div class="btn-group">
        {visit_btn}
        {call_btn}
      </div>
      <a href="https://www.google.com/search?q={google_search.replace(' ', '+')}" target="_blank" rel="noopener" class="update-link">See on Google &rarr;</a>
      <a href="#" class="update-link owner-only" id="updateLink" style="display:none;">Update listing</a>
      <a href="#" class="delete-link owner-only" id="deleteLink" style="display:none;">Remove listing</a>
    </div>
  </aside>
</div>
<footer>
  <div class="footer-inner">
    <a href="/index.html" style="font-family:'Playfair Display',serif;color:#fff;font-size:16px;text-decoration:none;">Newcastle<span style="color:var(--gold)">Local</span></a>
    <div class="footer-links">
      <a href="#">About</a>
      <a href="/list.html">List Your Business</a>
      <a href="#">Privacy</a>
      <a href="#">Contact</a>
    </div>
    <div>&copy; 2025 NewcastleLocal &middot; {plural} directory &middot; Data sourced from public records</div>
  </div>
</footer>
<script>
(function(){{
  var params = new URLSearchParams(location.search);
  var key = params.get('key');
  var body = document.querySelector('.profile-body');
  var slug = body.dataset.slug;
  var dataKey = body.dataset.key;
  if (key && key === dataKey) {{
    var base = 'https://splendid-salamander-8c08bf.netlify.app';
    document.getElementById('updateLink').href = base + '/update/?slug=' + slug + '&key=' + key + '&cat={cat}';
    document.getElementById('deleteLink').href = base + '/.netlify/functions/delete-listing?slug=' + slug + '&key=' + key + '&cat={cat}';
    document.querySelectorAll('.owner-only').forEach(function(el) {{ el.style.display = 'block'; }});
  }}
  fetch('/data/{cat}.json?v=' + Date.now())
    .then(function(r) {{ return r.json(); }})
    .then(function(data) {{
      var listing = data.listings.find(function(l) {{ return l.slug === slug; }});
      if (!listing) return;
      var badge = document.getElementById('statusBadge');
      if (listing.status === 'active') {{
        badge.style.background = '#e8f5e9'; badge.style.color = '#2e7d32'; badge.textContent = '✓ Active listing';
      }} else {{
        badge.style.background = '#f5f5f5'; badge.style.color = '#888'; badge.textContent = 'Contact to confirm';
      }}
    }}).catch(function(){{}});
}})();
</script>
</body>
</html>"""
    return html


def update_json(cat, new_listings):
    json_path = f"/tmp/seo-work2/data/{cat}.json"
    with open(json_path, "r") as f:
        data = json.load(f)
    
    existing_slugs = {l["slug"] for l in data["listings"]}
    added = 0
    
    for b in new_listings:
        if b["slug"] in existing_slugs:
            print(f"  SKIP (already exists): {b['slug']}")
            continue
        
        secret_key = make_key(b["slug"])
        b["secret_key"] = secret_key
        
        entry = {
            "name": b["name"],
            "credentials": b.get("credentials", ""),
            "address": b["address"],
            "suburb": b["suburb"],
            "phone": b.get("phone", ""),
            "website": b.get("website", ""),
            "services": b.get("services", []),
            "service_areas": b.get("service_areas", []),
            "status": "active",
            "hours": b.get("hours", "Mon-Fri 9:00am-5:00pm"),
            "description": b.get("description", ""),
            "featured": False,
            "slug": b["slug"],
            "secret_key": secret_key,
            "last_verified": TODAY,
            "google_search": b.get("google_search", ""),
        }
        if b.get("email"):
            entry["email"] = b["email"]
        
        data["listings"].append(entry)
        added += 1
        print(f"  Added to JSON: {b['slug']}")
    
    data["meta"]["total"] = len(data["listings"])
    data["meta"]["last_updated"] = TODAY
    
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)
    
    return added


def create_profile_html(cat, b):
    secret_key = b["secret_key"]
    slug = b["slug"]
    html = generate_html(cat, b, secret_key)
    
    out_dir = f"/tmp/seo-work2/profiles/{cat}"
    os.makedirs(out_dir, exist_ok=True)
    
    out_path = f"{out_dir}/{slug}.html"
    with open(out_path, "w") as f:
        f.write(html)
    print(f"  Created HTML: {out_path}")


def update_sitemap(new_urls):
    sitemap_path = "/tmp/seo-work2/sitemap.xml"
    with open(sitemap_path, "r") as f:
        content = f.read()
    
    new_entries = []
    for url in new_urls:
        entry = f"""  <url>
    <loc>{url}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>"""
        if url not in content:
            new_entries.append(entry)
    
    if new_entries:
        insert_before = "</urlset>"
        new_content = content.replace(insert_before, "\n".join(new_entries) + "\n" + insert_before)
        with open(sitemap_path, "w") as f:
            f.write(new_content)
        print(f"  Added {len(new_entries)} URLs to sitemap")
    
    return len(new_entries)


# Main execution
random.seed(42)  # reproducible keys
all_new_urls = []

for cat, businesses in NEW_BUSINESSES.items():
    print(f"\n=== {cat.upper()} ===")
    
    # Step 1: update JSON and get secret keys assigned
    added_count = update_json(cat, businesses)
    
    # Reload JSON to get the secret keys
    json_path = f"/tmp/seo-work2/data/{cat}.json"
    with open(json_path, "r") as f:
        data = json.load(f)
    slug_to_key = {l["slug"]: l["secret_key"] for l in data["listings"]}
    
    # Step 2: create HTML for each new business
    for b in businesses:
        slug = b["slug"]
        if slug in slug_to_key:
            b["secret_key"] = slug_to_key[slug]
        else:
            b["secret_key"] = make_key(slug)
        create_profile_html(cat, b)
        all_new_urls.append(f"https://newcastlelocal.com.au/profiles/{cat}/{slug}.html")

print("\n=== SITEMAP ===")
update_sitemap(all_new_urls)

print(f"\n=== DONE ===")
print(f"Total new profile URLs: {len(all_new_urls)}")
for url in all_new_urls:
    print(f"  {url}")

