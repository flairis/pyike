import React, { useEffect, useState } from "react";
import { FunctionDefinition } from "../markdoc/tags/function.markdoc";
import { CodeBlock } from "./CodeBlock";

export function FunctionReference({ href, children }) {
    const [func, setFunc] = useState(null);

    useEffect(() => {
        console.log(href)
        fetch(`/.cache/${href}.json`)
            .then((response) => response.json())
            .then((json) => setFunc(json as FunctionDefinition))
            .catch((error) => console.error("Error fetching the file:", error));
    }, []);

    return (
        <div>
            <h1>{func?.name ?? "Loading"}</h1>
            <CodeBlock data-language="python">{func ? func.signature : "Loading"}</CodeBlock>
            <p>{func?.summary ?? "Loading"}</p>
            <p>{func?.desc ?? ""}</p>
            <h2>Arguments</h2>
            {func?.args.length > 0 ? (
                <ul>
                    {func.args.map((arg, index) => (
                        <li key={index}>
                            <b>{arg.name}</b>: {arg.type ?? "any"} - {arg.desc}
                        </li>
                    ))}
                </ul>
            ) : (
                <p>No arguments available.</p>
            )}
            <h2>Returns</h2>
            <p>{func?.returns ?? "Loading"}</p>
            <h2>Examples</h2>
            {func?.examples.length > 0 ? (
                <ul>
                    {func.examples.map((example, index) => (
                        <>
                            <p>{example.desc}</p >
                            <CodeBlock data-language="python">{example ? example.code : "Loading"}</CodeBlock>
                        </>
                    ))}
                </ul>
            ) : (
                <p>No arguments available.</p>
            )
            }
        </div >
    );
}

export default FunctionReference;
