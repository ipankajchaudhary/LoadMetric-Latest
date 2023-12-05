import React from 'react'
import 'react-tabulator/lib/styles.css' // default theme
import 'react-tabulator/css/bootstrap/tabulator_bootstrap.min.css' // use Theme(s)

import { ReactTabulator, reactFormatter } from 'react-tabulator'

function SimpleButton(props) {

  const cellValue = props.cell._cell.value

  if(cellValue > 0){
    return <p  className = "text-danger">▲</p>
  }
  else{
    return <p className='text-success'>▼</p>

  }
}

class TaskTable extends React.Component {
  state = {
    data: this.props.data,
    threshold: this.props.formData.thresholdValue,
    isFirstTime: this.props.formData.isFirstTime,
    divColor: 'initial-color',
    selectedName: ''
  }
  ref = null

  getColumns = () => {
    const baseColumns = [
      { title: 'Measure', field: 'Measure', width: 200 },
      { title: 'Dimension Name', field: 'DimensionName', width: 200 },
      { title: 'Column Name', field: 'ColumnName', width: 150 },
      { title: 'LoadTime', field: 'LoadTime', width: 150 }
    ]

    if (!this.state.isFirstTime) {
      baseColumns.push(
        {
          title: 'Previous Load Time',
          field: 'PreviousLoadTime',
          width: 200
        },
        {
          title: 'Change in Load Time',
          field: 'ChangeinLoadTime',
          width: 200,
          formatter: reactFormatter(<SimpleButton />)
        }
      )
    }

    // Add the remaining columns
    baseColumns.push(
      { title: 'Report Name', field: 'ReportName', width: 150 },
      { title: 'Page Name', field: 'PageName', width: 175 },
      { title: 'Visual Name', field: 'VisualName', width: 125 },
      { title: 'Visual Title', field: 'VisualTitle', width: 150 }
    )

    return baseColumns
  }

  rowClick = (e, row) => {
    this.setState({ selectedName: row.getData().name })
  }

  setData = () => {
    this.setState(this.props.data)
  }

  clearData = () => {
    this.setState({ data: [] })
  }

  render() {
    const rowFormatter = row => {
      const data = row.getData()

      if (data.LoadTime === this.state.threshold) {
        row.getElement().style.backgroundColor = 'red'
      }
    }
    const options = {
      height: 200,
      movableRows: true,
      movableColumns: true
    }

    return (
      <div className="mt-5 mx-2 border">
        <ReactTabulator
          columns={this.getColumns()} // Use the dynamically generated columns
          data={this.props.data}
          footerElement={<span>Footer</span>}
          rowFormatter={rowFormatter}
        />
      </div>
    )
  }
}

export default TaskTable
