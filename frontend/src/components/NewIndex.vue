<template>
  <body>
    <div v-if="isConectionNotMade" v-on:keyup.enter="inputParams">
      <br />
      <br />
      <h3>In order for us to get started, please provide the below information.</h3>
      <div>
        <input
          class="input_base_url"
          name="sesamBaseURL"
          ref="sesamBaseURL"
          value="Type in your SESAM base url, i.e. https://datahub-1abcde007.sesam.cloud/api"
        />
        <br />
        <h3>Type in your SESAM JWT in the field below.</h3>
        <input
          name="sesamJWT"
          ref="sesamJWT"
          value="Type in the password as well"
          type="password"
        />
        <br />
        <button v-on:click.prevent="inputParams">Fetch SESAM</button>
      </div>
    </div>
    <div class="split left" v-if="isConnectionMade">
        <br />
        <h3>Pipes currently in SESAM</h3>
        <br />
        <br />
        <div class="checkboxes">
        <li class="list" v-for="(pipe, index) in scan_pipes" :key="index">
            <input
            :id="pipe"
            :value="pipe"
            name="table"
            type="checkbox"
            class="checkbox"
            v-model="selected_pipes"
            />
            {{ pipe }}
        </li>
        </div> 
        <br />
        <br />
        <br />
          <li class="list_select_all">
            <input
              type="radio"
              class="checkbox_select_all"
              v-on:click="selectAll"
            />
            {{ this.select_all_string }}
          </li>
        <br />       
    </div>
    <div class="split right" v-if="isConnectionMade">
        <br />
        <h3>Automagic choice</h3>
        <br />
        <button class="choice_button" v-on:click.prevent="createTestData">Embed pipes with testdata</button>
        <br />
        <button class="choice_button" v-on:click.prevent="mergeIntoGlobals">Merge into globals</button>
        <br />
        <button class="choice_button" v-on:click.prevent="connectToDatabase">Connect to database</button>
        <br />
        <img
          class="sesam_base_img"
          src="https://sesam.io/images/Hub1.png"
          alt="sesam_base_img"
        />     
    </div>
    <div v-if="isSesamResponse" class="modelling">
      <br />
      <br />
      <h3>{{ result["sesam_result"] }}</h3>
      <h3>Follow the below link to look at your new data!</h3>
      <br />
      <a href="https://portal.sesam.io/dashboard">Sesam Portal</a>
    </div>
    <div v-if="isBufferActive" class="center" id="Buffer">
      <span v-html="bufferIcon()"></span>
    </div>
    <div v-if="is404" class="center">
        <span v-for="(pipe, index) in scan_pipes" :key="index">
            {{ pipe }}
        </span>
    </div>
    <div v-if="isCleanSesam" class="center">
      <br />
        <h3 v-for="(pipe, index) in scan_pipes" :key="index">
          {{ pipe }}
      </h3>
      <br />
      <button class="db_button" v-on:click.prevent="connectToDatabase">Connect to database</button>
    </div>
    <div>
      <component
        :selected_pipes="selected_pipes"
        class="component"
        v-if="isMergeOfGlobals"
        :is="nextComponent"
      ></component>
    </div>
    <div>
      <component
        :selected_pipes="selected_pipes"
        class="component"
        v-if="isDbConnect"
        :is="dbComponent"
      ></component>
    </div>
  </body>
</template>
  
  <script>
import api from "../api";
import Globals from "./NewGlobals";
import DatabaseConnect from "./NewDbConnect";
export default {
  name: "NewIndex",
  data: () => {
    return {
      isDbConnect: false,
      isMergeOfGlobals: false,
      isCheckAll: false,
      is404: false,
      isCleanSesam: false,
      isConectionNotMade: true,
      isSesamResponse: false,
      isConnectionMade: false,
      isBufferActive: false,
      result: "{{result}}",
      select_all_string: "Select All",
      scan_pipes: [],
      selected_pipes: [],
      nextComponent: "Globals",
      dbComponent: "DatabaseConnect",
    };
  },
  components: {
    Globals,
    DatabaseConnect,
  },
  methods: {
    bufferIcon() {
      return '<img src="https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif" alt="Loading GIF">';
    },
    mergeIntoGlobals() {
      this.isMergeOfGlobals = true;
      this.isConectionNotMade = false;
      this.isConnectionMade = false;
    },
    connectToDatabase() {
      this.isDbConnect = true;
      this.isCleanSesam = false;
      this.isConectionNotMade = false;
      this.isConnectionMade = false;
    },
    selectAll() {
      this.isCheckAll = !this.isCheckAll;
      this.selected_pipes = [];
      if(this.isCheckAll){ // Check all
        this.selected_pipes = this.scan_pipes;
      }
    },
    async inputParams() {
      let sesamBaseURL = this.$refs.sesamBaseURL.value;
      let sesamJWT = this.$refs.sesamJWT.value;
      this.isConectionNotMade = false;
      this.isBufferActive = true;
      await fetch("http://localhost:5000/get_all_pipes", {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          sesamBaseURL: sesamBaseURL,
          sesamJWT: sesamJWT,
        }),
      });
      this.sesamResponse();
    },
    sesamResponse() {
      api.getResource("/sesam_response").then((data) => {
          //eslint-disable-next-line no-console
          //console.log("testing this...");
          //eslint-disable-next-line no-console
          //console.log(data["result"][0]);
          if (data["result"][0] == "Could not fetch pipes from Sesam."){
            this.scan_pipes = data["result"];
            this.is404 = true;
            this.isBufferActive = false;
            data = null;
          }
          if (data["result"][0] == "It seems you have not started using SESAM yet."){
            this.scan_pipes = data["result"];
            this.isCleanSesam = true;
            this.isBufferActive = false;
            data = null;
          }
          if (data != null && data != "") {
            this.scan_pipes = data["result"];
            this.isConnectionMade = true;
            this.isBufferActive = false;
          }
      });
    },
    async createTestData() {
      let pipes = this.selected_pipes;
      this.isConnectionMade = false;
      this.isBufferActive = true;
      await fetch("http://localhost:5000/create_testdata", {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          pipes: pipes,
        }),
      });
      this.globalResponse();
    },
    globalResponse() {
      api.getResource("/sesam_response").then((data) => {
        if (data != null && data != "") {
          //eslint-disable-next-line no-console
          //console.log("testing this...");
          //eslint-disable-next-line no-console
          //console.log(data);
          this.result = data;
          this.isSesamResponse = true;
          this.isBufferActive = false;
        }
      });
    },
  },
};
</script>
  
<style>

.sesam_base_img {
  margin-top: 10%;
  height: auto;
  width: 400px;
}

.modelling {
  padding: 10%;
}

.left {
  left: 0;
}

.right {
  right: 0;
}

.split {
  height: 100%;
  width: 50%;
  position: fixed;
  z-index: 1;
  top: 20;
  overflow-x: hidden;
  padding-top: 20px;
}

.checkboxes {
  height: 450px;
  overflow-y: scroll;
}
.checkboxes input {
  vertical-align: middle;
}
.checkboxes label span {
  vertical-align: middle;
}

.checkbox_option {
  text-align: center;
  width: 5%;
  background: #fff;
}

.checkbox_select_all {
  width: 5%;
  background: #fff;
  vertical-align: middle;
}

.list_select_all {
  font-size: 12px;
  text-align: center;
  display: block;
}

.list {
  font-size: 12px;
  text-align: left;
  display: block;
}

body {
  background-color: rgb(255, 255, 255);
  box-sizing: border-box;
  color: rgb(61, 57, 53);
  display: block;
  font-family: museo-sans-rounded, sans-serif;
  font-size: 14px;
  font-style: normal;
  height: 720px;
  letter-spacing: 0.2px;
  line-height: 10px;
  margin-bottom: 0px;
  margin-left: 0px;
  margin-right: 0px;
  margin-top: 0px;
  text-size-adjust: 100%;
  width: 100%;
}

button {
  width: 15%;
  margin: 5px;
  padding: 5px 10px;
  font-size: 12px;
  letter-spacing: 1px;
  background: #009fdf;
  height: 40px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #fff;
  -webkit-transition: all 0.1s ease-in-out;
  -moz-transition: all 0.1s ease-in-out;
  -ms-transition: all 0.1s ease-in-out;
  -o-transition: all 0.1s ease-in-out;
  transition: all 0.1s ease-in-out;
}

.choice_button {
  width: 38%;
  padding: 5px 10px;
  font-size: 12px;
  letter-spacing: 1px;
  background: #009fdf;
  height: 40px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #fff;
  -webkit-transition: all 0.1s ease-in-out;
  -moz-transition: all 0.1s ease-in-out;
  -ms-transition: all 0.1s ease-in-out;
  -o-transition: all 0.1s ease-in-out;
  transition: all 0.1s ease-in-out;
}

input {
  padding: 5%;
  text-align: center;
  width: 20%;
  height: 40px;
  padding: 5px 10px;
  font-size: 12px;
  letter-spacing: 1px;
  background: #fff;
  border: 2px solid #fff;
}

.input_base_url {
  padding: 5%;
  text-align: center;
  width: 40%;
  height: 40px;
  padding: 5px 10px;
  font-size: 12px;
  letter-spacing: 1px;
  background: #fff;
  border: 2px solid #fff;
}

.db_button {
  width: 18%;
  padding: 5px 10px;
  font-size: 12px;
  letter-spacing: 1px;
  background: #009fdf;
  height: 40px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #fff;
  -webkit-transition: all 0.1s ease-in-out;
  -moz-transition: all 0.1s ease-in-out;
  -ms-transition: all 0.1s ease-in-out;
  -o-transition: all 0.1s ease-in-out;
  transition: all 0.1s ease-in-out;
}
</style>