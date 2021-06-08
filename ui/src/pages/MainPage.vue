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
        <el-row>
          <el-col :span="2" :offset='19'><el-button type="primary" icon="el-icon-search" size="medium">查询</el-button></el-col>
          <el-col :span="2"><el-button type="primary" size="medium">导出Excel</el-button></el-col>
        </el-row>
        <el-row>
          <el-table :data="tableData" border style="width: 100%">
            <el-table-column prop="id" label="序号" width="180"></el-table-column>
            <el-table-column prop="date" label="显示名" width="180"></el-table-column>
            <el-table-column prop="name" label="SAM账户名" width="180"></el-table-column>
            <el-table-column prop="create_time" label="创建时间"></el-table-column>
            <el-table-column prop="belongsto" label="隶属于"></el-table-column>
            <el-table-column prop="ou" label="组织单位"></el-table-column>
          </el-table>
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
        value: '选项1',
        label: '常规报表',
        children: [{
          value: '子选项1',
          label: '所有用户'
        }, {
          value: '子选项2',
          label: '同时在多个组的用户'
        }, {
          value: '子选项3',
          label: '最近删除的用户'
        }, {
          value: '子选项4',
          label: '最近创建的用户'
        }, {
          value: '子选项5',
          label: '最近更改的用户'
        }]
      }, {
        value: '选项2',
        label: '账户状态报表',
        children: [{
          value: '子选项6',
          label: '被禁用的用户'
        }, {
          value: '子选项7',
          label: '被锁定的用户'
        }, {
          value: '子选项8',
          label: '账户过期的用户'
        }]
      }, {
        value: '选项3',
        label: '登录报表',
        children: [{
          value: '子选项9',
          label: '非活动/休眠用户'
        }, {
          value: '子选项10',
          label: '实际最后登录'
        }, {
          value: '子选项11',
          label: '最近登录的用户'
        }, {
          value: '子选项12',
          label: '基于登录时间的报表'
        }, {
          value: '子选项13',
          label: '已启动的用户'
        }]
      }],
      tableData: [],
      value1: 'corp.gwm.cn',
      reportType: '',
      table_set1: [],
      table_set2: [],
      table_set3: [],
      table_set4: [],
      list_data: [],
      condition: {
        domain: ''
      },
      table_display: 'first'
    }
  },
  mounted () {
    this.drawUserReport()
    this.drawSystemReport()
    this.drawLoggedOnUserReport()
    this.drawGroupAndOUReport()
  },
  methods: {
    handleClick: function (tab, event, domain) {
      console.log(tab, event)
      if (this.table_display === 'first') {
        console.log(this.condition.domain)
        this.$http.post('search_statistic_data', {condition: this.condition}).then(res => {
          this.list_data = res.data
          this.table_set1 = this.list_data.slice(0, 4)
          this.table_set2 = this.list_data.slice(5, 8)
        })
      }
    },
    handleChange: function (domain, reportType) {
      console.log(domain, reportType)
    },
    drawUserReport: function () {
      let userReports = this.$echarts.init(document.getElementById('UserReport'), 'light')
      userReports.setOption({
        title: {
          text: 'User Report'
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
        title: { text: 'System Report' },
        tooltip: {},
        xAxis: {
          data: ['计算机', '被禁用计算机', '工作站', '域控制器']
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
          source: [
            ['amount', 'usertype'],
            [11100, '从未登录过'],
            [1000, '最近30天内登录'],
            [2280, '30天内密码即将过期']
          ]
        },
        title: { text: 'Logged On User Report' },
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
          source: [
            ['amount', 'grouptype'],
            [3677, '组数量'],
            [3333, '安全组'],
            [1555, '通讯组'],
            [222, '无成员组'],
            [1333, '组织单位']
          ]
        },
        title: { text: 'Group And OU Report' },
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
