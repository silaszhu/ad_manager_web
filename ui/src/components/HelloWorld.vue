<template>
<el-container>
  <el-main>
    <el-row>
      <el-col :span="4" :offset="20">
      <el-select v-model="condition.domain" placeholder="请选择" size="small">
      <el-option v-for="item in options" :key="item.value1" :label="item.label" :value="item.value1"></el-option>
      </el-select></el-col>
    </el-row>
    <el-tabs v-model="table_display" type="card" @tab-click="handleClick">
      <el-tab-pane label="AD概览" name="first">
        <el-row :gutter="20">
          <el-col :span="11" :offset="1"><div id="UserReport" :style="{width: '550px', height: '350px'}"></div></el-col>
          <el-col :span="11"><div id="SystemReport" :style="{width: '550px', height: '350px'}"></div></el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="11" :offset="1"><div id="LoggedOnUserReport" :style="{width: '550px', height: '350px'}"></div></el-col>
          <el-col :span="11"><div id="GroupAndOUReport" :style="{width: '550px', height: '350px'}"></div></el-col>
        </el-row>
      </el-tab-pane>
      <el-tab-pane label="AD报表" name="second">报表类型：
        <el-cascader v-model="reportType" :options="reportTypes" @change="handleChange"></el-cascader>
        <div style="margin: 15px 0;"></div>
        <el-row v-show="isShow">
        日期范围：<el-date-picker v-model="start_end_date" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" style="left: 4px;"></el-date-picker>
        </el-row>
        <div style="margin: 15px 0;"></div>
        <el-row>
        <el-checkbox :indeterminate="isIndeterminate" v-model="checkAll" @change="handleCheckAllChange">全选</el-checkbox>
        <div style="margin: 10px 0;"></div>
        <el-checkbox-group v-model="checkedAttrs" @change="handleCheckedAttrsChange" :style="{width: '1000px'}">
          <el-checkbox v-for="attr in attrs" :label="attr" :key="attr">{{attr}}</el-checkbox>
        </el-checkbox-group>
        </el-row>
        <el-row>
          <el-col :span="2" :offset='19'><el-button type="primary" icon="el-icon-search" size="medium" @click="handleSearchClick">查询</el-button></el-col>
          <el-col :span="2"><el-button type="primary" size="medium" @click="downloadExcel">导出Excel</el-button></el-col>
         </el-row>
        <div style="margin: 15px 0;"></div>
        <el-row>
          <el-table :data="tableData" :fit=true :stripe=true border style="width: 100%">
            <template v-for="(col ,index) in columns"><el-table-column :prop="col.name" :label="col.value" v-bind:key="index"></el-table-column></template>
          </el-table>
          <div style="margin: 15px 0;"><el-pagination background layout="prev, pager, next" :current-page="currentPage" :total="total" @prev-click="handlePreClick" @next-click="handleNextClick"></el-pagination></div>
        </el-row>
      </el-tab-pane>
    </el-tabs>
  </el-main>
</el-container>
</template>

<style>
  .el-menu-vertical-demo:not(.el-menu--collapse) {
    width: 2000px;
    min-height: 400px;
  }
</style>

<script>
export default {
  name: 'MainPage',
  data () {
    return {
      options: [{
        value1: 'corp.gwm.cn',
        label: 'corp.gwm.cn'
      }, {
        value1: 'tech.gwm.cn',
        label: 'tech.gwm.cn'
      }, {
        value1: 'global.gwm.cn',
        label: 'global.gwm.cn'
      }],
      reportTypes: [{
        value: 'normal_reports',
        label: '常规报表',
        children: [{
          value: 'all_user',
          label: '所有用户'
        }, {
          value: 'recent_create_user',
          label: '最近创建的用户'
        }, {
          value: 'recent_update_user',
          label: '最近更改的用户'
        }]
      }, {
        value: 'account_reports',
        label: '账户状态报表',
        children: [{
          value: 'forbidden_user',
          label: '被禁用的用户'
        }, {
          value: 'lock_user',
          label: '被锁定的用户'
        }, {
          value: 'expire_user',
          label: '账户过期的用户'
        }]
      }, {
        value: 'login_reports',
        label: '登录报表',
        children: [{
          value: 'sleep_user',
          label: '非活动/休眠用户'
        }, {
          value: 'login_time',
          label: '基于登录时间的报表'
        }, {
          value: 'start_user',
          label: '已启动的用户'
        }]
      }],
      tableData: [],
      reportType: [],
      table_set1: [],
      table_set2: [],
      table_set3: [],
      table_set4: [],
      list_data: [],
      condition: {
        domain: 'corp.gwm.cn'
      },
      table_display: 'first',
      start_end_date: '',
      checkAll: false,
      checkedAttrs: [],
      attrs: [],
      isIndeterminate: true,
      isShow: false,
      columns: [],
      currentPage: 1,
      total: 10
    }
  },
  mounted () {
    this.drawUserReport()
    this.drawSystemReport()
    this.drawLoggedOnUserReport()
    this.drawGroupAndOUReport()
    this.fetchData()
    this.renderFieldsList()
  },
  watch: {
    table_set1: function () {
      this.drawUserReport()
    },
    table_set2: function () {
      this.drawSystemReport()
    },
    table_set3: function () {
      this.drawLoggedOnUserReport()
    },
    table_set4: function () {
      this.drawGroupAndOUReport()
    }
  },
  methods: {
    handleClick: function (tab, event) {
      console.log(tab, event)
      this.fetchData()
    },
    handleChange: function (domain, reportType) {
      console.log(domain, reportType)
      this.renderFieldsList(reportType)
    },
    renderFieldsList: function (reportType) {
      this.$http.post('search_fields', {report_type: this.reportType}).then(res => {
        this.attrs = res.data.message
        this.isShow = res.data.is_show
        this.columns = res.data.report_fields
        console.log(this.attrs)
      }
      )
    },
    handleSearchClick: function () {
      console.log(this.reportType)
      if (this.table_display === 'second') {
        console.log(this.condition.domain)
        console.log(this.start_end_date)
        this.$http.post('search_reports_dataset',
          {condition: {domain: this.condition.domain, report_type: this.reportType, checkedAttrs: this.checkedAttrs, start_end_date: this.start_end_date, page: this.currentPage}}).then(res => {
          this.tableData = res.data.message
          this.columns = res.data.report_fields
          this.currentPage = this.currentPage
          this.total = res.data.result_list_count
          console.log(this.tableData)
        })
      }
    },
    handlePreClick: function () {
      this.$http.post('search_reports_dataset',
        {condition: {domain: this.condition.domain, report_type: this.reportType, checkedAttrs: this.checkedAttrs, start_end_date: this.start_end_date, page: (this.currentPage - 1)}}).then(res => {
        this.tableData = res.data.message
        this.columns = res.data.report_fields
        this.currentPage = this.currentPage - 1
        console.log(this.tableData)
      })
    },
    handleNextClick: function () {
      this.$http.post('search_reports_dataset',
        {condition: {domain: this.condition.domain, report_type: this.reportType, checkedAttrs: this.checkedAttrs, start_end_date: this.start_end_date, page: (this.currentPage + 1)}}).then(res => {
        this.tableData = res.data.message
        this.columns = res.data.report_fields
        this.currentPage = this.currentPage + 1
        console.log(this.tableData)
      })
    },
    downloadExcel: function () {
      console.log('download excel')
      this.$http.post('download_excel',
        {condition: {domain: this.condition.domain, report_type: this.reportType, checkedAttrs: this.checkedAttrs, start_end_date: this.start_end_date}}, {responseType: 'blob'}).then(res => {
        const blob = new Blob([res.data])
        var sFM = 'YYYYMMDDhhmmss'
        var df = this.$moment().format(sFM) + ''
        var fileName = df + '.xlsx'
        const elink = document.createElement('a')
        elink.download = fileName
        elink.style.display = 'none'
        elink.href = URL.createObjectURL(blob)
        document.body.appendChild(elink)
        elink.click()
        URL.revokeObjectURL(elink.href)
        document.body.removeChild(elink)
      })
    },
    handleCheckAllChange (val) {
      this.checkedAttrs = val ? this.attrs : []
      this.isIndeterminate = false
    },
    handleCheckedAttrsChange (value) {
      let checkedCount = value.length
      this.checkAll = checkedCount === this.attrs.length
      this.isIndeterminate = checkedCount > 0 && checkedCount < this.attrs.length
    },
    fetchData: function () {
      if (this.table_display === 'first') {
        console.log(this.condition.domain)
        this.$http.post('search_statistic_data', {condition: this.condition}).then(res => {
          this.list_data = res.data.message
          this.table_set1 = this.list_data.slice(0, 4)
          this.table_set2 = this.list_data.slice(4, 9)
        })
        this.$http.post('search_statistic_data2', {condition: this.condition}).then(res => {
          this.list_data = res.data.message
          this.table_set3 = this.list_data.slice(0, 4)
          this.table_set4 = this.list_data.slice(4, 10)
        })
      }
    },
    drawUserReport: function () {
      let userReports = this.$echarts.init(document.getElementById('UserReport'), 'light')
      userReports.setOption({
        title: {
          text: '用户报表'
        },
        tooltip: {},
        xAxis: {
          data: ['用户总数', '被禁用', '被锁定', '密码已过期']
        },
        legend: {
          data: ['用户量']
        },
        yAxis: {},
        series: [{
          name: '用户量',
          type: 'bar',
          data: this.table_set1
        }]
      })
    },
    drawSystemReport () {
      let SystemReport = this.$echarts.init(document.getElementById('SystemReport'))
      SystemReport.setOption({
        title: { text: '系统报表' },
        tooltip: {},
        xAxis: {
          data: ['计算机', '被禁用计算机', '服务器', '域控制器']
        },
        legend: {
          data: ['机器数量']
        },
        yAxis: {},
        series: [{
          name: '机器数量',
          type: 'bar',
          data: this.table_set2
        }]
      })
    },
    drawLoggedOnUserReport () {
      let LoggedOnUserReport = this.$echarts.init(document.getElementById('LoggedOnUserReport'))
      LoggedOnUserReport.setOption({
        dataset: {
          source: this.table_set3
        },
        title: { text: '登录用户报表' },
        tooltip: {},
        legend: {
          data: ['登录态']
        },
        xAxis: {},
        yAxis: {
          type: 'category',
          axisLabel: {
            interval: 0,
            rotate: 70
          }
        },
        series: [
          {
            name: '登录态',
            type: 'bar',
            encode: {
              x: 'amount',
              y: 'usertype'
            }
          }
        ]
      })
    },
    drawGroupAndOUReport () {
      let GroupAndOUReport = this.$echarts.init(document.getElementById('GroupAndOUReport'), 'light')
      GroupAndOUReport.setOption({
        dataset: {
          source: this.table_set4
        },
        title: { text: '组和组织单位报表' },
        tooltip: {},
        legend: {
          data: ['组数量']
        },
        xAxis: {},
        yAxis: {
          type: 'category',
          axisLabel: {
            interval: 0,
            rotate: 40
          }
        },
        series: [
          {
            name: '组数量',
            type: 'bar',
            encode: {
              x: 'amount',
              y: 'grouptype'
            }
          }
        ]
      })
    }
  }
}

</script>
