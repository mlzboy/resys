using System;
using System.Collections.Generic;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;
using org.phprpc;
using org.phprpc.util;
public partial class _Default : System.Web.UI.Page
{
    protected void Page_Load(object sender, EventArgs e)
    {

    }
	protected void Button1_Click(object sender, EventArgs e)
	{

            PHPRPC_Client client = new PHPRPC_Client("http://10.3.11.99");
            this.Response.Write(PHPConvert.ToString(client.Invoke("Hi", new Object[] {"Ma Bingyao"})));
			
		recommend("product1324",10,"userid=-1");


		//int[] a = new int[10];
			//Random r = new Random();
			//for (int i = 0; i < 10; i++)
			//{
			//    a[i] = r.Next();
			//}
			//a = (int[])PHPConvert.ToArray(client.Invoke("Sort", new Object[] {a}), typeof(int[]));
			//for (int i = 0; i < 10; i++)
			//{
			//    Console.Write(a[i] + "\r\n");
			//}
			//Console.ReadLine();
    }
	/// <summary>
	/// 根据传入的productid,userid来返回相关的推荐产品7位id有序列表
	/// </summary>
	/// <param name="productid">用户目前正在浏览的页面的产品7位id,不含尺寸</param>
	/// <param name="topn">设置返回推荐结果条数</param>
	/// <param name="userid">userid为-1表示不只使用productid来推荐</param>
	/// <returns></returns>
	private IList<string> recommend(string productid,int topn,string userid)
	{
		PHPRPC_Client client = new PHPRPC_Client("http://10.3.11.99");
		object result = client.Invoke("recommend", new Object[] {productid, topn,userid});
		AssocArray ht = PHPConvert.ToAssocArray(result);
		//this.Response.Write(ht.Count);

		foreach (int s in ht.Keys)
		{
			this.Response.Write(string.Format("{0}",s.ToString()));
		}
		this.Response.Write("<br/>");
		IList<string> tops=new List<string>();
		for(int i=0;i<ht.Count;i++)
		{
			string elem = PHPConvert.ToString(ht[i]);
			tops.Add(elem);
			this.Response.Write(string.Format("{0}<br/>", elem));
		}
		return tops;
	}
}
