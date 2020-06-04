# SolData is reading data from a KLNE Inverter 3000 and send a JSON structure to a NATS server

The program is now running as a service and writes data to a file every 10 seconds
The current format of the file is commaseparated including some text to explain the value

ToDo
* Change the file format to JSON
* Publish the data to a NATS service
* Performance optimization. Currently the file is open and closed for each roundtrip. 
  This should be changed to keep the file open until the data changes.
  When we pass midnight, the current file must be closed and a new file created.
  
