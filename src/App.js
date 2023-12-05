import React, { Fragment, useState } from "react";
import InputScreen from "./Components/InputScreen";
import TableComponent from "./Components/TableComponent";
import "./App.css";
import LoadingSpinner from "./Components/Spinner";
import LinearWithValueLabel from "./Components/ProgressBar";
import CircularWithValueLabel from "./Components/ProgressBar";

const App = () => {
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [progress, setProgress] = useState(0)
  const [formData, setFormdata] = useState({});
  const handleFormSubmit = (formData) => {


    console.log(formData)
    setLoading(true);
    setFormdata(formData);
    fetch("http://127.0.0.1:3002/progress", {
      method: "POST",
      body: JSON.stringify(formData),
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        setProgress(JSON.parse(data).result)
      })
      .catch((error) => {
        console.error("Error:", error);
        alert(error);
      });


    setTimeout(() => {
      fetch("http://127.0.0.1:3002/data", {
        method: "POST",
        body: JSON.stringify(formData),
        headers: {
          "Content-Type": "application/json",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          console.log(response)
          setResponse(JSON.parse(data));
          setLoading(false);
        })
        .catch((error) => {
          console.error("Error:", error);
          alert(error);
        });
    }, 100000);
    // setLoading(true);
    // setFormdata(formData);
  };
  console.log(response)

  return (

    <Fragment>
      {/* <Titlebar /> */}
      <div>
        {loading ? (
          <div>
            <LinearWithValueLabel totalprogress={progress} />
          </div>
        ) : response ? (
          <TableComponent response={response} formData={formData} />
        ) : (
          <InputScreen handleFormSubmit={handleFormSubmit} />
        )}
      </div>
    </Fragment>
  );
};

export default App;
