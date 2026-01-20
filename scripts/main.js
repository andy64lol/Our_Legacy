console.log("Scripts from Our Legacy are activated!");

events.on("playerJoin", (player) => {
    console.log("Welcome back, legend.");
});

//this script is called when a flag from main.py is passed, if you want the script to iterate after every action is done, then add the script to /scripts/iterated_scripts.json