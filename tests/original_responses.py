test_default_employee_listing = {'data': [
    {'empid': 499999, 'bdt': '1958-05-01', 'fnm': 'Sachin', 'lnm': 'Tsukuda', 'gdr': 'M', 'hdt': '1997-11-30'},
    {'empid': 499998, 'bdt': '1956-09-05', 'fnm': 'Patricia', 'lnm': 'Breugel', 'gdr': 'M', 'hdt': '1993-10-13'},
    {'empid': 499997, 'bdt': '1961-08-03', 'fnm': 'Berhard', 'lnm': 'Lenart', 'gdr': 'M', 'hdt': '1986-04-21'},
    {'empid': 499996, 'bdt': '1953-03-07', 'fnm': 'Zito', 'lnm': 'Baaz', 'gdr': 'M', 'hdt': '1990-09-27'},
    {'empid': 499995, 'bdt': '1958-09-24', 'fnm': 'Dekang', 'lnm': 'Lichtner', 'gdr': 'F', 'hdt': '1993-01-12'},
    {'empid': 499994, 'bdt': '1952-02-26', 'fnm': 'Navin', 'lnm': 'Argence', 'gdr': 'F', 'hdt': '1990-04-24'},
    {'empid': 499993, 'bdt': '1963-06-04', 'fnm': 'DeForest', 'lnm': 'Mullainathan', 'gdr': 'M', 'hdt': '1997-04-07'},
    {'empid': 499992, 'bdt': '1960-10-12', 'fnm': 'Siamak', 'lnm': 'Salverda', 'gdr': 'F', 'hdt': '1987-05-10'},
    {'empid': 499991, 'bdt': '1962-02-26', 'fnm': 'Pohua', 'lnm': 'Sichman', 'gdr': 'F', 'hdt': '1989-01-12'},
    {'empid': 499990, 'bdt': '1963-11-03', 'fnm': 'Khaled', 'lnm': 'Kohling', 'gdr': 'M', 'hdt': '1985-10-10'}],
    'currentPageSize': 10, 'currentPageNumber': 1, 'hasNext': True,
    'totalCount': 300024}

test_default_employee_listing_gender_filter = {'data': [
    {'empid': 499999, 'bdt': '1958-05-01', 'fnm': 'Sachin', 'lnm': 'Tsukuda', 'gdr': 'M', 'hdt': '1997-11-30'}],
    'currentPageSize': 1, 'currentPageNumber': 1, 'hasNext': True,
    'totalCount': 179973}

test_default_employee_listing_birth_date_filter = {'data': [
    {'empid': 499999, 'bdt': '1958-05-01', 'fnm': 'Sachin', 'lnm': 'Tsukuda', 'gdr': 'M', 'hdt': '1997-11-30'}],
    'currentPageSize': 1, 'currentPageNumber': 1, 'hasNext': True,
    'totalCount': 76}

test_default_employee_listing_first_name_filter = {'data': [
    {'empid': 499999, 'bdt': '1958-05-01', 'fnm': 'Sachin', 'lnm': 'Tsukuda', 'gdr': 'M', 'hdt': '1997-11-30'}],
    'currentPageSize': 1, 'currentPageNumber': 1, 'hasNext': True,
    'totalCount': 955}

test_default_employee_listing_last_name_filter = {'data': [
    {'empid': 499999, 'bdt': '1958-05-01', 'fnm': 'Sachin', 'lnm': 'Tsukuda', 'gdr': 'M', 'hdt': '1997-11-30'}],
    'currentPageSize': 1, 'currentPageNumber': 1, 'hasNext': True,
    'totalCount': 185}

test_employee_listing_with_custom_field = {'data': [
    {'empid': 499999, 'bdt': '1958-05-01', 'gdr': 'M', 'hdt': '1997-11-30',
     'flnm': 'Sachin Tsukuda'}], 'currentPageSize': 1, 'currentPageNumber': 1, 'hasNext': True, 'totalCount': 185}
