import React, { useEffect, useState } from 'react'
import { Button, IconButton, Popover, Typography } from '@mui/material'
import FilterListIcon from '@mui/icons-material/FilterList'
import TaskTable from './TaskTable'

const TableComponent = ({ response, formData }) => {

  var data = response.result
  const [selectedMeasure, setSelectedMeasure] = useState('')
  const [selectedDimension, setSelectedDimension] = useState('')
  const [selectedReport, setSelectedReport] = useState('')
  const [selectedVisual, setSelectedVisual] = useState('')
  const [selectedPage, setSelectedPage] = useState('')
  const [filteredData, setFilteredData] = useState(data)
  const [filterdimensionCheckboxFlag, setFilterdimensionCheckboxFlag] =
    useState(false)
  const [anchorEl, setAnchorEl] = useState(null)

  const [
    filterthresholdCheckboxFlag,
    setFilterthresholdCheckboxFlag
  ] = useState(false)


  const [filtervisualCheckboxFlag, setFiltervisualCheckboxFlag] =
    useState(false)

  const measures = [...new Set(response.result.map(item => item.Measure))]
  const dimensions = [
    ...new Set(response.result.map(item => item.DimensionName))
  ]
  const reports = [...new Set(response.result.map(item => item.ReportName))]
  const visuals = [...new Set(response.result.map(item => item.VisualName))]
  const pages = [...new Set(response.result.map(item => item.PageName))]


  const handleClick = event => {
    setAnchorEl(event.currentTarget)
  }

  const handleClose = () => {
    setAnchorEl(null)
  }

  const open = Boolean(anchorEl)
  const id = open ? 'simple-popover' : undefined


  function filterTableData(
    measure,
    dimension,
    report,
    visual,
    page,
  ) {
    const filtered = data.filter(item => {
      return (
        (measure === '' || item.Measure === measure) &&
        (dimension === '' || item.DimensionName === dimension) &&
        (report === '' || item.ReportName === report) &&
        (visual === '' || item.VisualName === visual) &&
        (page === '' || item.PageName === page)

      )
    })
    setFilteredData(filtered)
  }
  const handlethresholdCheckboxChange = event => {
    setFilterthresholdCheckboxFlag(event.target.checked)

    setFilteredData(
      data.filter(item => {
        return !filterthresholdCheckboxFlag ? item.LoadTime === (formData.thresholdValue) : true
      })
    )
  }

  const handledimensionCheckboxChange = event => {
    setFilterdimensionCheckboxFlag(event.target.checked)
    setFilteredData(
      data.filter(item => {
        return !filterdimensionCheckboxFlag ? item.hasDimension === '1' : true
      })
    )
  }



  const handlevisualCheckboxChange = event => {
    setFiltervisualCheckboxFlag(event.target.checked)
    setFilteredData(
      data.filter(item => {
        return !filtervisualCheckboxFlag ? item.VisualName !== '-' : true
      })
    )
  }



  function handleMeasureChange(event) {
    setSelectedMeasure(event.target.value)
    filterTableData(
      event.target.value,
      selectedDimension,
      selectedReport,
      selectedVisual,
      selectedPage
    )
  }

  function handleDimensionChange(event) {
    setSelectedDimension(event.target.value)
    filterTableData(
      selectedMeasure,
      event.target.value,
      selectedReport,
      selectedVisual,
      selectedPage
    )
  }

  function handleReportChange(event) {
    setSelectedReport(event.target.value)
    filterTableData(
      selectedMeasure,
      selectedDimension,
      event.target.value,
      selectedVisual,
      selectedPage
    )
  }

  function handleVisualChange(event) {
    setSelectedVisual(event.target.value)
    filterTableData(
      selectedMeasure,
      selectedDimension,
      selectedReport,
      event.target.value,
      selectedPage
    )
  }

  function handlePageChange(event) {
    setSelectedPage(event.target.value)
    filterTableData(
      selectedMeasure,
      selectedDimension,
      selectedReport,
      selectedVisual,
      event.target.value
    )
  }

  return (
    <div className="container mt-5" style={{ maxWidth: 'fit-content' }}>
      <div className="Maindropdowncontainer d-flex justify-content-around">
        <div className="DropDownContainer mx-4">
          <div className="DropdownLabel mx-2"> Measure</div>
          <div className="Dropdown">
            <select
              value={selectedMeasure}
              onChange={handleMeasureChange}
              className="mx-2"
            >
              <option value=""> All Measures</option>
              {measures.map((measure, index) => (
                <option key={index} value={measure}>
                  {measure}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="DropDownContainer mx-4">
          <div className="DropdownLabel mx-2">Dimension </div>
          <div className="Dropdown">
            <select
              value={selectedDimension}
              onChange={handleDimensionChange}
              className="mx-2"
            >
              <option value=""> All Dimensions</option>
              {dimensions.map((dimension, index) => (
                <option key={index} value={dimension}>
                  {dimension}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="DropDownContainer mx-4">
          <div className="DropdownLabel mx-2">Report </div>
          <div className="Dropdown">
            <select
              value={selectedReport}
              onChange={handleReportChange}
              className="mx-2"
            >
              <option value="">All Reports</option>
              {reports.map((report, index) => (
                <option key={index} value={report}>
                  {report}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="DropDownContainer mx-4">
          <div className="DropdownLabel mx-2">Page </div>
          <div className="Dropdown">
            <select
              value={selectedPage}
              onChange={handlePageChange}
              className="mx-2"
            >
              <option value="">All Pages</option>
              {pages.map((page, index) => (
                <option key={index} value={page}>
                  {page}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="DropDownContainer mx-4">
          <div className="DropdownLabel mx-2">Visual </div>
          <div className="Dropdown">
            <select
              value={selectedVisual}
              onChange={handleVisualChange}
              className="mx-2"
            >
              <option value="">All Visuals</option>
              {visuals.map((visual, index) => (
                <option key={index} value={visual}>
                  {visual}
                </option>
              ))}
            </select>
          </div>
        </div>
        <Button
          aria-describedby={id}
          variant="contained"
          onClick={handleClick}
          className="mx-2 popoverBtn"
        >
          <IconButton>
            <FilterListIcon />
          </IconButton>
        </Button>
        <Popover
          id={id}
          style={{ display: 'flex', flexDirection: 'row' }}
          open={open}
          anchorEl={anchorEl}
          onClose={handleClose}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'left'
          }}
        >
          <Typography sx={{ p: 2 }} className='d-flex flex-column'>

            <label>
              <input
                type="checkbox"
                checked={filterthresholdCheckboxFlag}
                onChange={handlethresholdCheckboxChange}
                className='mx-2'
              />
              Above Threshold
            </label>
            <label>
              <input
                type="checkbox"
                checked={filterdimensionCheckboxFlag}
                onChange={handledimensionCheckboxChange}
                className='mx-2'
              />
              Measure With Dimensions
            </label>
            <label>
              <input
                type="checkbox"
                checked={filtervisualCheckboxFlag}
                onChange={handlevisualCheckboxChange}
                className='mx-2'
              />
              Measure With Visuals
            </label>
          </Typography>
        </Popover>
      </div>
      <div className="cards">
        <div className="carD px-5">
          <div className="card total_measures  rounded-0 ">
            <div className="card-body">
              <h4 className="card-text">

                <b>Total Measure Combination</b>
              </h4>
              <h3 className="card-title mb-auto">{response.result.length}</h3>
            </div>
          </div>
        </div>

        <div className="carD px-5">
          <div className="card combinations_below_threshold  rounded-0">
            <div className="card-body">
              <h4 className="card-text">

                <b>Combinations below threshold</b>
              </h4>
              <h3 className="card-title mb-auto">
                {
                  response.result
                    .map(entry => entry.LoadTime)
                    .filter(e => e < formData.thresholdValue).length
                }
              </h3>
            </div>
          </div>
        </div>
        <div className="carD px-5">
          <div className="card combinations_above_threshold  rounded-0">
            <div className="card-body">
              <h4 className="card-text">

                <b>Combinations above threshold</b>
              </h4>
              <h3 className="card-title mb-auto">
                {
                  response.result
                    .map(entry => entry.LoadTime)
                    .filter(e => e === formData.thresholdValue).length
                }
              </h3>
            </div>
          </div>
        </div>
      </div>
      <div className="table mt-3" style={{ overflowY: 'auto', height: '67vh' }}>
        <TaskTable data={filteredData} formData={formData} />
      </div>
    </div>
  )
}

export default TableComponent
