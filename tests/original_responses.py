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

test_default_employee_listing_asc_sorted = {
    'data': [{'empid': 10001, 'bdt': '1953-09-02', 'fnm': 'Georgi', 'lnm': 'Facello', 'gdr': 'M', 'hdt': '1986-06-26'},
             {'empid': 10002, 'bdt': '1964-06-02', 'fnm': 'Bezalel', 'lnm': 'Simmel', 'gdr': 'F', 'hdt': '1985-11-21'},
             {'empid': 10003, 'bdt': '1959-12-03', 'fnm': 'Parto', 'lnm': 'Bamford', 'gdr': 'M', 'hdt': '1986-08-28'},
             {'empid': 10004, 'bdt': '1954-05-01', 'fnm': 'Chirstian', 'lnm': 'Koblick', 'gdr': 'M',
              'hdt': '1986-12-01'},
             {'empid': 10005, 'bdt': '1955-01-21', 'fnm': 'Kyoichi', 'lnm': 'Maliniak', 'gdr': 'M',
              'hdt': '1989-09-12'},
             {'empid': 10006, 'bdt': '1953-04-20', 'fnm': 'Anneke', 'lnm': 'Preusig', 'gdr': 'F', 'hdt': '1989-06-02'},
             {'empid': 10007, 'bdt': '1957-05-23', 'fnm': 'Tzvetan', 'lnm': 'Zielinski', 'gdr': 'F',
              'hdt': '1989-02-10'},
             {'empid': 10008, 'bdt': '1958-02-19', 'fnm': 'Saniya', 'lnm': 'Kalloufi', 'gdr': 'M', 'hdt': '1994-09-15'},
             {'empid': 10009, 'bdt': '1952-04-19', 'fnm': 'Sumant', 'lnm': 'Peac', 'gdr': 'F', 'hdt': '1985-02-18'},
             {'empid': 10010, 'bdt': '1963-06-01', 'fnm': 'Duangkaew', 'lnm': 'Piveteau', 'gdr': 'F',
              'hdt': '1989-08-24'}], 'currentPageSize': 10, 'currentPageNumber': 1, 'hasNext': True,
    'totalCount': 300024}

test_dept_emp_mapping_page_resp = {'data': [
    {'fnm': 'Sachin', 'lnm': 'Tsukuda', 'dpnm': 'Production', 'frmdt': '1997-11-30', 'tdt': '9999-01-01',
     'hrdt': '1997-11-30'}], 'currentPageSize': 1, 'currentPageNumber': 1, 'hasNext': True, 'totalCount': 331603}

test_dept_emp_mapping_full_name_filter_resp = {'data': [
    {'fnm': 'Sumant', 'lnm': 'Prochazka', 'dpnm': 'Sales', 'frmdt': '1999-05-16', 'tdt': '2000-01-24',
     'hrdt': '1986-10-05'}], 'currentPageSize': 1, 'currentPageNumber': 1, 'hasNext': True, 'totalCount': 14}

test_custom_field_extractor = {'data': [
    {'fnm': 'Sachin', 'lnm': 'Tsukuda', 'dpnm': 'Production', 'frmdt': '1997-11-30', 'tdt': '9999-01-01',
     'hrdt': '1997-11-30'}], 'currentPageSize': 1, 'currentPageNumber': 1, 'hasNext': True, 'totalCount': 198850}

test_string_contains_filter = {'data': [
    {'fnm': 'Bangqing', 'lnm': 'Kleiser', 'dpnm': 'Sales', 'frmdt': '1988-07-25', 'tdt': '2001-10-09',
     'hrdt': '1986-06-06'}], 'currentPageSize': 1, 'currentPageNumber': 1, 'hasNext': True, 'totalCount': 52245}

test_string_like_filter = {
    'data': [{'empid': 499999, 'fnm': 'Sachin', 'lnm': 'Tsukuda', 'gdr': 'M', 'desg': 'Engineer'}],
    'currentPageSize': 1, 'currentPageNumber': 1, 'hasNext': True, 'totalCount': 115003}

test_greater_than_filter = {'data': [
    {'fnm': 'Bikash', 'lnm': 'Covnot', 'dpnm': 'Quality Management', 'frmdt': '2000-02-01', 'tdt': '2000-05-19',
     'hrdt': '2000-01-28'}], 'currentPageSize': 1, 'currentPageNumber': 1, 'hasNext': False, 'totalCount': 1}

test_less_than_filter = {'data': [
    {'fnm': 'Aimee', 'lnm': 'Baja', 'dpnm': 'Marketing', 'frmdt': '1985-02-06', 'tdt': '1985-02-17',
     'hrdt': '1985-02-06'}], 'currentPageSize': 1, 'currentPageNumber': 1, 'hasNext': False, 'totalCount': 1}

test_greater_than_equal_to_filter = {'data': [
    {'fnm': 'Sachin', 'lnm': 'Tsukuda', 'dpnm': 'Production', 'frmdt': '1997-11-30', 'tdt': '9999-01-01',
     'hrdt': '1997-11-30'}], 'currentPageSize': 1, 'currentPageNumber': 1, 'hasNext': True, 'totalCount': 240124}

test_less_than_equal_to_filter = {'data': [
    {'fnm': 'Aimee', 'lnm': 'Baja', 'dpnm': 'Marketing', 'frmdt': '1985-02-06', 'tdt': '1985-02-17',
     'hrdt': '1985-02-06'}], 'currentPageSize': 1, 'currentPageNumber': 1, 'hasNext': False, 'totalCount': 1}

test_has_field_value_filter = {'data': [
    {'fnm': 'Sachin', 'lnm': 'Tsukuda', 'dpnm': 'Production', 'frmdt': '1997-11-30', 'tdt': '9999-01-01',
     'hrdt': '1997-11-30'}], 'currentPageSize': 1, 'currentPageNumber': 1, 'hasNext': True, 'totalCount': 331603}

test_has_none_value_filter = {'data': [], 'currentPageSize': 1, 'currentPageNumber': 1, 'hasNext': False,
                              'totalCount': 0}

test_inequality_filter = {'data': [
    {'fnm': 'Dekang', 'lnm': 'Lichtner', 'dpnm': 'Production', 'frmdt': '1997-06-02', 'tdt': '9999-01-01',
     'hrdt': '1993-01-12'}], 'currentPageSize': 1, 'currentPageNumber': 1, 'hasNext': True, 'totalCount': 132753}

test_indata_filter = {'data': [
    {'fnm': 'Dekang', 'lnm': 'Lichtner', 'dpnm': 'Production', 'frmdt': '1997-06-02', 'tdt': '9999-01-01',
     'hrdt': '1993-01-12'},
    {'fnm': 'Dekang', 'lnm': 'Bage', 'dpnm': 'Production', 'frmdt': '1987-03-24', 'tdt': '9999-01-01',
     'hrdt': '1987-03-24'}], 'currentPageSize': 10, 'currentPageNumber': 1, 'hasNext': False, 'totalCount': 2}

test_unix_between_filter = {'data': [], 'currentPageSize': 1, 'currentPageNumber': 1, 'hasNext': False, 'totalCount': 0}


test_default_employee_listing_without_count = {'data': [
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
    'currentPageSize': 10, 'currentPageNumber': 1, 'hasNext': True}
