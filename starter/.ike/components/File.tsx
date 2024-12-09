import React, { useEffect, useState } from "react";

export function File({ href, children }) {
    const [data, setData] = useState(null);

    useEffect(() => {
        fetch("/data.json")
            .then((response) => response.json())
            .then((json) => setData(json))
            .catch((error) => console.error("Error fetching the file:", error));
    }, []);

    return (
        <div>
            <h1>Local File Data:</h1>
            {data ? <pre>{JSON.stringify(data, null, 2)}</pre> : "Loading..."}
        </div>
    );
}

export default File;
