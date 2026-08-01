DATA CLEANING ERRORS NOTED
- Null values in admin1 and admin2, lattitude and longitude for Hola(Tana River)
- Cleaned by: adding in values for the specified fields

- Data type for date is string instead of datetime
- Cleaned by: changing the datatype

- Units standardization: some contain numeric values rather than the raw units (e.g., 20KG)
- Cleaned by using a regex match to divide the values by the numeric part to obtain the singular units