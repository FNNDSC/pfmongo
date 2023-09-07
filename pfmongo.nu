source env.nu

# Check if the response json from the PurpleAir API contains
# a 'false' status. If so, quit, showing the response and
# an error message.
def response_checkForError [
    response: record	# The response from the remote API call.
] {
    if not $response.status {
    	print $response
    	print $response.response
    	let span = (metadata $response).span
      	error make {
    	    msg: "Error in communicating with purple air API",
    	    label: {
    	        text: "origin",
    		start: $span.start
    		end: $span.end
    	    }
    	}
    }
    $response
}

# The interface/call to the pfmongo app that communicates with
# the PurpleAir API to get sensor data for a given sensor.
def pfmongo_sensorDataGet [
    idx:int	# The index of the sensor in the purpleair DB.
] {
    (response_checkForError (pfmongo --sensorDataGet $idx | from json))
}

# The interface/call to the pfmongo app that communicates with
# the PurpleAir API to get the list of sensors in a group.
def pfmongo_DBlist[
    group:int	# The ID of the sensor group in the purpleair DB.
] {
    (response_checkForError (pfmongo --sensorsInGroupList --usingGroupID $group | from json))
}

# Get the list all sensors in a PurpleAir API group
def sensors_list_inGroup [
    group:int	# The group ID
] {
    let sensors = ((pfmongo_sensorsInGroupList $group) | get response | get members)
    return $sensors
}
