import csv, math, random, os

random.seed(42)
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample_climate_data.csv')

# ── 500 cities across all continents ─────────────────────────────────────────
# Format: (name, lat, lon)
CITIES = [
# North America (80)
('New York',40.71,-74.01),('Los Angeles',34.05,-118.24),('Chicago',41.88,-87.63),
('Houston',29.76,-95.37),('Phoenix',33.45,-112.07),('Philadelphia',39.95,-75.17),
('San Antonio',29.42,-98.49),('San Diego',32.72,-117.16),('Dallas',32.78,-96.80),
('San Jose',37.34,-121.89),('Austin',30.27,-97.74),('Jacksonville',30.33,-81.66),
('San Francisco',37.77,-122.42),('Columbus',39.96,-82.99),('Charlotte',35.23,-80.84),
('Indianapolis',39.77,-86.16),('Seattle',47.61,-122.33),('Denver',39.74,-104.98),
('Nashville',36.17,-86.78),('Oklahoma City',35.47,-97.52),('El Paso',31.76,-106.49),
('Boston',42.36,-71.06),('Portland',45.52,-122.68),('Las Vegas',36.17,-115.14),
('Memphis',35.15,-90.05),('Louisville',38.25,-85.76),('Baltimore',39.29,-76.61),
('Milwaukee',43.04,-87.91),('Albuquerque',35.08,-106.65),('Tucson',32.22,-110.97),
('Atlanta',33.75,-84.39),('Miami',25.77,-80.19),('Minneapolis',44.98,-93.27),
('New Orleans',29.95,-90.07),('Cleveland',41.50,-81.69),('Tampa',27.95,-82.46),
('Pittsburgh',40.44,-79.99),('Sacramento',38.58,-121.49),('Kansas City',39.10,-94.58),
('Salt Lake City',40.76,-111.89),('Toronto',43.65,-79.38),('Montreal',45.50,-73.57),
('Vancouver',49.28,-123.12),('Calgary',51.05,-114.07),('Edmonton',53.55,-113.49),
('Ottawa',45.42,-75.69),('Winnipeg',49.90,-97.14),('Quebec City',46.81,-71.21),
('Hamilton',43.26,-79.87),('Kitchener',43.45,-80.49),('Mexico City',19.43,-99.13),
('Guadalajara',20.67,-103.35),('Monterrey',25.67,-100.31),('Puebla',19.04,-98.20),
('Tijuana',32.53,-117.04),('Leon',21.12,-101.68),('Ciudad Juarez',31.74,-106.49),
('Havana',23.13,-82.38),('Santiago de Cuba',20.02,-75.82),('Guatemala City',14.64,-90.51),
('San Salvador',13.69,-89.19),('Tegucigalpa',14.10,-87.21),('Managua',12.13,-86.28),
('San Jose CR',9.93,-84.08),('Panama City',8.99,-79.52),('Santo Domingo',18.48,-69.90),
('Port-au-Prince',18.54,-72.34),('Kingston',17.99,-76.79),('San Juan',18.47,-66.11),
('Belize City',17.25,-88.77),('Nassau',25.05,-77.35),('Bridgetown',13.10,-59.62),
('Port of Spain',10.65,-61.52),('Georgetown',6.80,-58.16),('Paramaribo',5.87,-55.17),
# South America (50)
('Bogota',4.71,-74.07),('Lima',-12.05,-77.04),('Buenos Aires',-34.60,-58.38),
('Rio de Janeiro',-22.91,-43.17),('Santiago',-33.45,-70.67),('Caracas',10.48,-66.88),
('Quito',-0.23,-78.52),('Montevideo',-34.90,-56.19),('Asuncion',-25.29,-57.65),
('La Paz',-16.50,-68.15),('Sao Paulo',-23.55,-46.63),('Brasilia',-15.78,-47.93),
('Salvador',-12.97,-38.50),('Fortaleza',-3.72,-38.54),('Belo Horizonte',-19.92,-43.94),
('Manaus',-3.10,-60.02),('Curitiba',-25.43,-49.27),('Recife',-8.05,-34.88),
('Porto Alegre',-30.03,-51.23),('Belem',-1.46,-48.50),('Medellin',6.25,-75.56),
('Cali',3.44,-76.52),('Barranquilla',10.96,-74.80),('Cartagena',10.40,-75.51),
('Guayaquil',-2.17,-79.92),('Cochabamba',-17.39,-66.16),('Santa Cruz',-17.80,-63.17),
('Arequipa',-16.41,-71.54),('Trujillo',-8.11,-79.03),('Maracaibo',10.63,-71.64),
('Valencia VE',10.18,-68.00),('Barquisimeto',10.07,-69.32),('Rosario',-32.95,-60.65),
('Cordoba AR',-31.42,-64.18),('Mendoza',-32.89,-68.84),('Tucuman',-26.82,-65.22),
('Mar del Plata',-38.00,-57.56),('Concepcion CL',-36.83,-73.05),('Valparaiso',-33.05,-71.62),
('Antofagasta',-23.65,-70.40),('Iquique',-20.21,-70.15),('Temuco',-38.74,-72.60),
('Asuncion PY',-25.29,-57.65),('Sucre',-19.04,-65.26),('Potosi',-19.59,-65.75),
('Cayenne',4.93,-52.33),('Paramaribo SR',5.87,-55.17),('Georgetown GY',6.80,-58.16),
('Montevideo UY',-34.90,-56.19),('Punta Arenas',-53.16,-70.91),
]
CITIES += [
# Europe (100)
('London',51.51,-0.13),('Paris',48.85,2.35),('Berlin',52.52,13.40),
('Madrid',40.42,-3.70),('Rome',41.90,12.50),('Moscow',55.75,37.62),
('Oslo',59.91,10.75),('Stockholm',59.33,18.07),('Warsaw',52.23,21.01),
('Vienna',48.21,16.37),('Amsterdam',52.37,4.90),('Brussels',50.85,4.35),
('Lisbon',38.72,-9.14),('Athens',37.98,23.73),('Budapest',47.50,19.04),
('Prague',50.08,14.44),('Bucharest',44.43,26.10),('Helsinki',60.17,24.94),
('Copenhagen',55.68,12.57),('Zurich',47.38,8.54),('Barcelona',41.39,2.15),
('Munich',48.14,11.58),('Hamburg',53.55,10.00),('Cologne',50.94,6.96),
('Frankfurt',50.11,8.68),('Stuttgart',48.78,9.18),('Dusseldorf',51.23,6.79),
('Dortmund',51.51,7.47),('Essen',51.46,7.01),('Leipzig',51.34,12.38),
('Dresden',51.05,13.74),('Hanover',52.37,9.73),('Nuremberg',49.45,11.08),
('Duisburg',51.43,6.76),('Bochum',51.48,7.22),('Wuppertal',51.26,7.15),
('Bielefeld',52.02,8.53),('Bonn',50.74,7.10),('Mannheim',49.49,8.47),
('Karlsruhe',49.01,8.40),('Milan',45.46,9.19),('Naples',40.85,14.27),
('Turin',45.07,7.69),('Palermo',38.12,13.36),('Genoa',44.41,8.93),
('Bologna',44.50,11.34),('Florence',43.77,11.25),('Bari',41.12,16.87),
('Catania',37.50,15.09),('Venice',45.44,12.33),('Seville',37.39,-5.99),
('Valencia ES',39.47,-0.38),('Bilbao',43.26,-2.93),('Zaragoza',41.65,-0.88),
('Malaga',36.72,-4.42),('Murcia',37.98,-1.13),('Palma',39.57,2.65),
('Porto',41.15,-8.61),('Braga',41.55,-8.43),('Coimbra',40.21,-8.43),
('Rotterdam',51.92,4.48),('The Hague',52.08,4.31),('Utrecht',52.09,5.12),
('Eindhoven',51.44,5.48),('Antwerp',51.22,4.40),('Ghent',51.05,3.72),
('Liege',50.63,5.57),('Bruges',51.21,3.22),('Lausanne',46.52,6.63),
('Geneva',46.20,6.15),('Basel',47.56,7.59),('Bern',46.95,7.45),
('Lyon',45.75,4.83),('Marseille',43.30,5.37),('Toulouse',43.60,1.44),
('Nice',43.71,7.26),('Nantes',47.22,-1.55),('Strasbourg',48.58,7.75),
('Bordeaux',44.84,-0.58),('Lille',50.63,3.06),('Rennes',48.11,-1.68),
('Reims',49.26,4.03),('Saint-Etienne',45.44,4.39),('Toulon',43.12,5.93),
('Grenoble',45.19,5.72),('Dijon',47.32,5.04),('Angers',47.47,-0.55),
('Vilnius',54.69,25.28),('Riga',56.95,24.11),('Tallinn',59.44,24.75),
('Minsk',53.90,27.57),('Kiev',50.45,30.52),('Kharkiv',49.99,36.23),
('Odessa',46.48,30.73),('Dnipro',48.46,35.04),('Donetsk',48.02,37.80),
('Lviv',49.84,24.03),('Chisinau',47.01,28.86),('Sofia',42.70,23.32),
('Zagreb',45.81,15.98),('Belgrade',44.80,20.46),('Sarajevo',43.85,18.36),
('Skopje',41.99,21.43),('Tirana',41.33,19.83),('Podgorica',42.44,19.26),
('Ljubljana',46.05,14.51),('Bratislava',48.15,17.11),('Tallinn EE',59.44,24.75),
]
CITIES += [
# Africa (80)
('Cairo',30.04,31.24),('Lagos',6.52,3.38),('Nairobi',-1.29,36.82),
('Cape Town',-33.93,18.42),('Casablanca',33.59,-7.62),('Addis Ababa',9.03,38.74),
('Accra',5.56,-0.20),('Dakar',14.72,-17.47),('Khartoum',15.55,32.53),
('Kinshasa',-4.32,15.32),('Dar es Salaam',-6.79,39.21),('Johannesburg',-26.20,28.04),
('Tunis',36.82,10.17),('Algiers',36.74,3.06),('Luanda',-8.84,13.23),
('Abidjan',5.35,-4.00),('Kampala',0.32,32.58),('Lusaka',-15.42,28.28),
('Harare',-17.83,31.05),('Maputo',-25.97,32.59),('Antananarivo',-18.91,47.54),
('Bamako',12.65,-8.00),('Conakry',9.54,-13.68),('Freetown',8.49,-13.23),
('Monrovia',6.30,-10.80),('Abuja',9.07,7.40),('Ibadan',7.38,3.90),
('Kano',12.00,8.52),('Kaduna',10.52,7.44),('Port Harcourt',4.77,7.01),
('Douala',4.05,9.70),('Yaounde',3.87,11.52),('Bangui',4.36,18.56),
('Brazzaville',-4.27,15.28),('Libreville',0.39,9.45),('Malabo',3.75,8.78),
('Lome',6.14,1.22),('Cotonou',6.37,2.42),('Porto-Novo',6.50,2.63),
('Ouagadougou',12.37,-1.53),('Niamey',13.51,2.11),('Ndjamena',12.11,15.04),
('Kigali',-1.95,30.06),('Bujumbura',-3.38,29.36),('Mogadishu',2.05,45.34),
('Djibouti',11.59,43.15),('Asmara',15.34,38.93),('Juba',4.85,31.62),
('Lilongwe',-13.97,33.79),('Blantyre',-15.79,35.00),('Gaborone',-24.65,25.91),
('Maseru',-29.32,27.48),('Mbabane',-26.32,31.14),('Windhoek',-22.56,17.08),
('Tripoli',32.90,13.18),('Benghazi',32.12,20.07),('Alexandria',31.20,29.92),
('Aswan',24.09,32.90),('Luxor',25.69,32.64),('Marrakech',31.63,-8.00),
('Fez',34.03,-5.00),('Tangier',35.78,-5.80),('Rabat',34.02,-6.83),
('Mombasa',-4.05,39.67),('Kisumu',-0.10,34.75),('Entebbe',0.05,32.46),
('Zanzibar',-6.16,39.19),('Arusha',-3.37,36.68),('Mwanza',-2.52,32.90),
('Durban',-29.86,31.02),('Pretoria',-25.75,28.19),('Port Elizabeth',-33.96,25.60),
('East London ZA',-33.02,27.91),('Bloemfontein',-29.12,26.21),('Kimberley',-28.74,24.77),
('Bulawayo',-20.15,28.58),('Mutare',-18.97,32.67),('Ndola',-12.97,28.64),
('Livingstone',-17.85,25.87),('Lubumbashi',-11.68,27.47),('Kisangani',0.52,25.19),
]
CITIES += [
# Asia (120)
('Tokyo',35.68,139.69),('Beijing',39.91,116.39),('Shanghai',31.23,121.47),
('Mumbai',19.08,72.88),('Delhi',28.61,77.21),('Dhaka',23.72,90.41),
('Karachi',24.86,67.01),('Bangkok',13.75,100.52),('Singapore',1.35,103.82),
('Jakarta',-6.21,106.85),('Manila',14.60,120.98),('Seoul',37.57,126.98),
('Taipei',25.05,121.53),('Kuala Lumpur',3.14,101.69),('Colombo',6.93,79.85),
('Kathmandu',27.72,85.32),('Kabul',34.53,69.17),('Tehran',35.69,51.42),
('Baghdad',33.34,44.40),('Riyadh',24.69,46.72),('Dubai',25.20,55.27),
('Islamabad',33.72,73.04),('Tashkent',41.30,69.27),('Ulaanbaatar',47.91,106.88),
('Yangon',16.87,96.19),('Osaka',34.69,135.50),('Nagoya',35.18,136.91),
('Sapporo',43.06,141.35),('Fukuoka',33.59,130.40),('Kobe',34.69,135.20),
('Kyoto',35.01,135.77),('Hiroshima',34.39,132.46),('Sendai',38.27,140.87),
('Chongqing',29.56,106.55),('Guangzhou',23.13,113.26),('Shenzhen',22.54,114.06),
('Wuhan',30.59,114.31),('Chengdu',30.57,104.07),('Tianjin',39.14,117.18),
('Xian',34.27,108.95),('Nanjing',32.06,118.78),('Hangzhou',30.25,120.16),
('Shenyang',41.80,123.43),('Harbin',45.75,126.64),('Qingdao',36.07,120.38),
('Zhengzhou',34.75,113.65),('Jinan',36.67,116.99),('Changsha',28.23,112.94),
('Kunming',25.05,102.71),('Urumqi',43.80,87.60),('Lhasa',29.65,91.13),
('Pyongyang',39.02,125.75),('Busan',35.10,129.04),('Incheon',37.46,126.71),
('Daegu',35.87,128.60),('Daejeon',36.35,127.38),('Gwangju',35.16,126.85),
('Ho Chi Minh City',10.82,106.63),('Hanoi',21.03,105.85),('Da Nang',16.07,108.22),
('Phnom Penh',11.57,104.92),('Vientiane',17.97,102.60),('Naypyidaw',19.74,96.13),
('Colombo LK',6.93,79.85),('Kandy',7.29,80.63),('Jaffna',9.67,80.02),
('Lahore',31.55,74.34),('Faisalabad',31.42,73.08),('Rawalpindi',33.60,73.04),
('Multan',30.20,71.47),('Hyderabad PK',25.37,68.37),('Peshawar',34.01,71.57),
('Quetta',30.19,67.01),('Ahmedabad',23.03,72.58),('Surat',21.17,72.83),
('Pune',18.52,73.86),('Jaipur',26.91,75.79),('Lucknow',26.85,80.95),
('Kanpur',26.46,80.35),('Nagpur',21.15,79.09),('Indore',22.72,75.86),
('Bhopal',23.26,77.40),('Patna',25.61,85.14),('Ludhiana',30.90,75.85),
('Agra',27.18,78.01),('Varanasi',25.32,83.01),('Madurai',9.93,78.12),
('Coimbatore',11.02,76.97),('Kochi',9.93,76.26),('Visakhapatnam',17.69,83.22),
('Kolkata',22.57,88.36),('Chennai',13.08,80.27),('Hyderabad IN',17.38,78.49),
('Bangalore',12.97,77.59),('Amman',31.95,35.93),('Beirut',33.89,35.50),
('Damascus',33.51,36.29),('Aleppo',36.20,37.16),('Ankara',39.93,32.86),
('Istanbul',41.01,28.95),('Izmir',38.42,27.14),('Bursa',40.19,29.06),
('Adana',37.00,35.32),('Gaziantep',37.07,37.38),('Konya',37.87,32.49),
('Baku',40.41,49.87),('Yerevan',40.18,44.51),('Tbilisi',41.69,44.83),
('Almaty',43.25,76.95),('Bishkek',42.87,74.59),('Dushanbe',38.56,68.77),
('Ashgabat',37.95,58.38),('Kabul AF',34.53,69.17),('Muscat',23.61,58.59),
('Manama',26.22,50.59),('Kuwait City',29.37,47.98),('Doha',25.29,51.53),
('Abu Dhabi',24.47,54.37),('Sanaa',15.35,44.21),('Aden',12.78,45.04),
]
CITIES += [
# Oceania (20)
('Sydney',-33.87,151.21),('Melbourne',-37.81,144.96),('Brisbane',-27.47,153.02),
('Perth',-31.95,115.86),('Adelaide',-34.93,138.60),('Canberra',-35.28,149.13),
('Darwin',-12.46,130.84),('Hobart',-42.88,147.33),('Gold Coast',-28.00,153.43),
('Newcastle AU',-32.93,151.78),('Auckland',-36.86,174.77),('Wellington',-41.29,174.78),
('Christchurch',-43.53,172.64),('Hamilton NZ',-37.79,175.28),('Tauranga',-37.69,176.17),
('Suva',-18.14,178.44),('Port Moresby',-9.44,147.18),('Noumea',-22.27,166.46),
('Honolulu',21.31,-157.86),('Papeete',-17.53,-149.57),
]

# Deduplicate by name
seen = set()
unique_cities = []
for c in CITIES:
    if c[0] not in seen:
        seen.add(c[0])
        unique_cities.append(c)
CITIES = unique_cities[:500]
print(f"City count: {len(CITIES)}")

# ── Generation ────────────────────────────────────────────────────────────────
def make_row(year, month, week, city, lat, lon, rng):
    base_temp  = 30 - abs(lat) * 0.55
    seasonal   = 14 * math.cos((month - 7) * math.pi / 6) * (1 if lat >= 0 else -1)
    trend      = (year - 1990) * 0.065
    temp       = round(base_temp + seasonal + trend + rng.gauss(0, 1.8), 2)
    precip_b   = max(10, 90 - abs(lat) * 0.8)
    precip     = round(max(0, precip_b/4 + 6*math.sin(month*math.pi/6) + rng.gauss(0, 8)), 2)
    wind       = round(max(0, 10 + abs(lat)*0.05 + rng.gauss(0, 3.5)), 2)
    humidity   = round(min(100, max(5, 75 - abs(lat)*0.4 + rng.gauss(0, 12))), 2)
    pressure   = round(1013.25 + rng.gauss(0, 8) - abs(lat)*0.05, 2)
    return [year, month, week, city, lat, lon, temp, precip, wind, humidity, pressure]

rng = random.Random(42)
rows = []
# 500 cities × 36 years × 12 months × 3 readings = 648,000 — trim to 500k
YEARS = range(1990, 2027)   # 37 years (1990–2026)
WEEKS = (1, 2, 3)           # 3 readings/month keeps total ~648k, we'll cap at 500k

for year in YEARS:
    for month in range(1, 13):
        for week in WEEKS:
            for city, lat, lon in CITIES:
                rows.append(make_row(year, month, week, city, lat, lon, rng))
                if len(rows) >= 700_000:
                    break
            if len(rows) >= 700_000: break
        if len(rows) >= 700_000: break
    if len(rows) >= 700_000: break

print(f"Rows generated: {len(rows):,}")

with open(OUT_PATH, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['year','month','week','city','latitude','longitude',
                'temperature','precipitation','wind_speed','humidity','pressure'])
    w.writerows(rows)

import os
size_mb = os.path.getsize(OUT_PATH) / 1024 / 1024
print(f"Written to: {OUT_PATH}")
print(f"File size:  {size_mb:.1f} MB")
