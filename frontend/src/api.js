// Interface against the backend, doing the network things


const sendData = (data) => {
    const params = location.href.split("?").at(-1);
    console.log(params);
    fetch("http://localhost:3001/?" + params, {
        headers : {"Content-Type" : "application/json"},
        method: "POST",
        body : JSON.stringify(data),
    })
};

export {sendData};