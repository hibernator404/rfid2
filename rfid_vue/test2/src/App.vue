<template>
  <div class="app-container">
    <nav class="navbar">
      <h1>打卡记录系统</h1>
      <button @click="fetchAttendanceData">获取数据</button>
      <input type="date" v-model="selectedDate" @change="filterData">
    </nav>

    <div class="main-content">
      <aside class="sidebar">
        <h2>员工列表</h2>
        <ul>
          <li v-for="(person, index) in uniquePersons" :key="index" @click="selectPerson(person)">
            {{ person }}
          </li>
        </ul>
      </aside>

      <section class="content">
        <div v-if="selectedPerson" class="person-card">
          <h2>{{ selectedPerson }} 的打卡记录</h2>
          <ul>
            <li v-for="record in selectedPersonFilteredRecords" :key="record.aid" class="record-item">
              <p><strong>员工ID:</strong> {{ record.userid }}</p>
              <p><strong>打卡日期:</strong> {{ record.createddate }}</p>
              <p><strong>上班时间:</strong> {{ formatTime(record.toworktimestamp) }}</p>
              <p><strong>下班时间:</strong> {{ formatTime(record.offworktimestamp) }}</p>
            </li>
          </ul>
          <p v-if="totalWorkSeconds[selectedPerson]">
            <strong>当日总工作时间:</strong> {{ formatSecondsToTime(totalWorkSeconds[selectedPerson]) }}
          </p>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import moment from 'moment';

export default {
  name: 'AttendanceData',
  data() {
    return {
      attendanceData: [],
      selectedDate: '',
      selectedPerson: null,
      filteredRecords: [],
      totalWorkSeconds: {} // 存储每个人员的总工作秒数的对象
    };
  },
  computed: {
    // 获取唯一的员工名单
    uniquePersons() {
      const uniqueNames = new Set();
      this.attendanceData.forEach(record => uniqueNames.add(record.username));
      return Array.from(uniqueNames);
    },
    selectedPersonFilteredRecords() {
      if (this.selectedPerson) {
        let filteredRecords = this.filteredRecords.filter(record => record.username === this.selectedPerson);

        if (this.selectedDate) {
          filteredRecords = filteredRecords.filter(record => record.createddate === this.selectedDate);
        }

        return filteredRecords;
      }
      return [];
    }
  },
  methods: {
    fetchAttendanceData() {
      axios.get('http://127.0.0.1:8088/attendance-data')
          .then(response => {
            if (Array.isArray(response.data)) {
              this.attendanceData = response.data;
              this.filteredRecords = response.data;
              this.calculateTotalWorkSeconds(this.selectedDate); // 在数据获取后计算总工作秒数
              // 设置默认选中第一个人员
              if (this.attendanceData.length > 0) {
                this.selectedPerson = this.attendanceData[0].username;
              }
            } else {
              console.error('返回的数据不是数组:', response.data);
            }
          })
          .catch(error => {
            console.error('获取打卡数据失败:', error);
          });
    },
    formatTime(timeString) {
      return moment(timeString).format('YYYY-MM-DD HH:mm:ss');
    },
    formatSecondsToTime(totalSeconds) {
      const hours = Math.floor(totalSeconds / 3600);
      const minutes = Math.floor((totalSeconds % 3600) / 60);
      const seconds = totalSeconds % 60;
      return `${hours}小时 ${minutes}分 ${seconds}秒`;
    },
    filterData() {
      // 清除已选的人员
      this.selectedPerson = null;

      // 等待 Vue 更新完成后再选择第一个人员
      this.$nextTick(() => {
        if (this.uniquePersons.length > 0) {
          this.selectedPerson = this.uniquePersons[0];
          this.calculateTotalWorkSeconds(this.selectedDate); // 在日期改变后重新计算总工作秒数
        }
      });
    },
    selectPerson(person) {
      this.selectedPerson = person;
      this.calculateTotalWorkSeconds(this.selectedDate); // 当选中人员时计算总工作秒数
    },
    calculateTotalWorkSeconds(selectedDate) {
      this.totalWorkSeconds = {}; // 清除之前的数据

      this.uniquePersons.forEach(person => {
        const records = this.attendanceData.filter(record => {
          return record.username === person && record.createddate === selectedDate;
        });

        let totalSeconds = 0;
        records.forEach(record => {
          if (record.toworktimestamp && record.offworktimestamp) {
            const start = moment(record.toworktimestamp);
            const end = moment(record.offworktimestamp);
            const duration = moment.duration(end.diff(start));
            totalSeconds += duration.asSeconds();
          }
        });

        // 四舍五入至0位小数
        this.totalWorkSeconds[person] = Math.round(totalSeconds);
      });
    }
  },
  created() {
    this.fetchAttendanceData();
  }
};
</script>

<style scoped>
/* 设置整个应用容器 */
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  font-family: Arial, sans-serif;
  position: fixed;
  left: 0;
  top: 0;
}

/* 导航栏样式 */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background-color: #333;
  color: #fff;
}

.navbar h1 {
  margin: 0;
}

.navbar button {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
  border-radius: 4px;
}

.navbar button:hover {
  background-color: #45a049;
}

.navbar input[type="date"] {
  padding: 8px;
  font-size: 16px;
  border-radius: 4px;
  border: 1px solid #ccc;
}

/* 主内容区域样式 */
.main-content {
  display: flex;
  flex: 1;
  background-color: #f0f0f0;
}

/* 侧边栏样式 */
.sidebar {
  width: 200px;
  background-color: #2c3e50;
  color: #ecf0f1;
  padding: 20px;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
}

.sidebar h2 {
  margin-top: 0;
}

.sidebar ul {
  list-style-type: none;
  padding: 0;
}

.sidebar ul li {
  padding: 10px 0;
  border-bottom: 1px solid #7f8c8d;
  cursor: pointer;
}

.sidebar ul li:hover {
  background-color: #34495e;
}

/* 内容区域样式 */
.content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  /* 自定义滚动条样式 */
  scrollbar-width: thin; /* "auto" 或 "thin" 适用于 Firefox */
  scrollbar-color: #888 #f0f0f0; /* 滚动条颜色 (拖动条, 背景) */
}

/* 自定义滚动条轨道 */
.content::-webkit-scrollbar-track {
  background: #f0f0f0; /* 轨道颜色 */
}

/* 自定义滚动条拖动条 */
.content::-webkit-scrollbar-thumb {
  background-color: #888; /* 拖动条颜色 */
  border-radius: 10px; /* 拖动条圆角 */
  border: 3px solid #f0f0f0; /* 拖动条边框 */
}

/* 人员卡片样式 */
.person-card {
  background-color: #fff;
  margin-bottom: 20px;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.person-card h2 {
  margin-top: 0;
}

.record-item {
  background-color: #ecf0f1;
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 4px;
}

.record-item p {
  margin: 5px 0;
}
</style>
