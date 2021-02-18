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
          src="data:image/png;base64,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"
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