import React, { useEffect, useState } from 'react'
import Select from 'react-select'


const InputScreen = ({ handleFormSubmit }) => {
  const [selectedFiles, setSelectedFiles] = useState('') 

  const [formData, setFormData] = useState({
    filePath: '',
    modelName: '',
    xmlaEndpoint: '',
    thresholdValue: '',
    isFirstTime: false
  })

  const handleChange = e => {
    const { name, value, type, checked } = e.target
    const fieldValue = type === 'checkbox' ? checked : value
    setFormData({ ...formData, [name]: fieldValue })
  }

  const handleSubmit = e => {
    e.preventDefault()
    handleFormSubmit(formData)
   
  }

  const handleChangeFile = e => {
    setSelectedFiles(e.map(e => e.value).join(','))
    setFormData({ ...formData, ['filePath']: e.map(e => e.value).join(',') })
  }

  console.log(selectedFiles)

  const [Filepath, setFilepath] = useState({ filepath: [] })
  const [options, setOptions] = useState([])

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const response = await fetch('http://127.0.0.1:3002/getreport')
        const result = await response.json()
        setFilepath(result)
      } catch (error) {
        console.error('Error fetching reports:', error)
      }
    }

    fetchReports()
  }, []) 

  useEffect(() => {
    const options = Filepath.filepath.map(pathArray => {
      const filePath = pathArray[0]
      const fileNameWithoutExtension = filePath
        .split('\\')
        .pop()
        .replace(/\..+$/, '')

      return {
        value: filePath,
        label: fileNameWithoutExtension
      }
    })

    setOptions(options)
  }, [Filepath]) 


  return (
    <div className="container">
      <h1>Metric Load Time Tool</h1>
      <form
        class="well form-horizontal mt-5"
        action="/submit"
        method="post"
        id="contact_form"
      >
        <fieldset>

          <div class="form-group d-flex">
            <label class="col-md-4 control-label">File Paths</label>
            <div class="col-md-8">
              <Select isMulti options={options} onChange={handleChangeFile} />
            </div>
          </div>

          <div class="form-group d-flex">
            <label class="col-md-4 control-label">Model Name</label>
            <div class="col-md-8">
              <input
                name="modelName"
                placeholder="Enter the Model Name"
                class="form-control"
                type="text"
                value={formData.modelName}
                onChange={handleChange}
              />
            </div>
          </div>

          <div class="form-group d-flex">
            <label class="col-md-4 control-label">XMLA Endpoint</label>
            <div class="col-md-8">
              <input
                name="xmlaEndpoint"
                placeholder="Enter the XMLA Endpoint of Workspace"
                class="form-control"
                value={formData.xmlaEndpoint}
                type="text"
                onChange={handleChange}
              />
            </div>
          </div>

          <div class="form-group d-flex">
            <label class="col-md-4 control-label">Threshold Value</label>
            <div class="col-md-8">
              <input
                name="thresholdValue"
                placeholder="Enter Threshold Value"
                class="form-control"
                value={formData.thresholdValue}
                type="text"
                onChange={handleChange}
              />
            </div>
          </div>

          <div class="form-group d-flex">
            <label class="col-md-4 control-label">
              Running for First Time?
            </label>
            <div class="col-md-8">
              <input
                type="checkbox"
                id="running_first_time"
                name="isFirstTime"
                value={formData.isFirstTime}
                onChange={handleChange}
              />
            </div>
          </div>

          <div class="form-group d-flex">
            <div class="col-md-8 col-md-offset-4">
              <button class="btn btn-success" onClick={handleSubmit}>
                Go!
              </button>
            </div>
          </div>
        </fieldset>
      </form>
    </div>
  )
}

export default InputScreen
